#!/usr/bin/env ruby
# frozen_string_literal: true

require 'json'
require 'net/http'
require 'open3'
require 'rexml/document'
require 'time'
require 'uri'

Release = Struct.new(
  :version, :published_at, :published_at_raw, :url, :length, :signature,
  keyword_init: true
)

SPARKLE_NAMESPACE = 'http://www.andymatuschak.org/xml-namespaces/sparkle'
DEFAULT_ENDPOINT = 'https://keyper.appitstudio.com/api/releases'

def required_text(item, xpath, version_hint)
  value = item.elements[xpath]&.text&.strip
  abort "Missing #{xpath} for #{version_hint}" if value.nil? || value.empty?
  value
end

def parse_releases(xml, source)
  document = REXML::Document.new(xml)
  items = document.get_elements('/rss/channel/item')
  abort "#{source}: appcast has no items" if items.empty?

  releases = items.map do |item|
    version = required_text(item, 'sparkle:version', 'unknown item')
    short_version = required_text(item, 'sparkle:shortVersionString', version)
    abort "#{source}: version mismatch for #{version}" unless short_version == version

    raw_date = required_text(item, 'pubDate', version)
    published_at = Time.rfc2822(raw_date)
    abort "#{source}: incorrect weekday in pubDate for #{version}" unless raw_date.start_with?(published_at.strftime('%a,'))

    enclosure = item.elements['enclosure']
    abort "#{source}: missing enclosure for #{version}" unless enclosure
    url = enclosure.attributes['url']&.strip
    length = enclosure.attributes['length']&.strip
    signature = enclosure.attributes['sparkle:edSignature']&.strip
    abort "#{source}: enclosure for #{version} must use HTTPS" unless URI.parse(url.to_s).is_a?(URI::HTTPS)
    abort "#{source}: invalid enclosure length for #{version}" unless length&.match?(/\A[1-9]\d*\z/)
    abort "#{source}: missing Ed25519 signature for #{version}" if signature.nil? || signature.empty?

    Release.new(
      version: version,
      published_at: published_at,
      published_at_raw: raw_date,
      url: url,
      length: length,
      signature: signature
    )
  rescue ArgumentError, URI::InvalidURIError => e
    abort "#{source}: invalid metadata for #{version || 'unknown item'}: #{e.message}"
  end

  versions = releases.map(&:version)
  abort "#{source}: duplicate versions: #{versions.tally.select { |_version, count| count > 1 }.keys.join(', ')}" unless versions.uniq.length == versions.length
  abort "#{source}: items must be newest-first by pubDate" unless releases.each_cons(2).all? { |newer, older| newer.published_at > older.published_at }
  releases
rescue REXML::ParseException => e
  abort "#{source}: malformed XML: #{e.message}"
end

def load_git_appcast(ref)
  xml, status = Open3.capture2('git', 'show', "#{ref}:appcast.xml")
  abort "Unable to read appcast.xml from #{ref}" unless status.success?
  parse_releases(xml, ref)
end

def verify_append_only(current, previous)
  current_by_version = current.to_h { |release| [release.version, release] }
  previous.each do |old|
    retained = current_by_version[old.version]
    abort "Append-only violation: removed release #{old.version}" unless retained

    fields = %i[published_at_raw url length signature]
    changed = fields.select { |field| retained.public_send(field) != old.public_send(field) }
    abort "Append-only violation: changed #{changed.join(', ')} for #{old.version}" unless changed.empty?
  end
end

def register_releases(releases)
  token = ENV['KEYPER_RELEASE_TOKEN'].to_s
  abort 'KEYPER_RELEASE_TOKEN is required for registration' if token.empty?
  endpoint = URI(ENV.fetch('KEYPER_RELEASE_ENDPOINT', DEFAULT_ENDPOINT))
  abort 'Keyper release endpoint must use HTTPS' unless endpoint.is_a?(URI::HTTPS)

  releases.reverse_each do |release|
    request = Net::HTTP::Post.new(endpoint)
    request['Authorization'] = "Bearer #{token}"
    request['Content-Type'] = 'application/json'
    request.body = JSON.generate(
      version: release.version,
      released_at: release.published_at.utc.iso8601
    )

    response = Net::HTTP.start(
      endpoint.host,
      endpoint.port,
      use_ssl: true,
      open_timeout: 10,
      read_timeout: 20
    ) { |http| http.request(request) }
    abort "Keyper rejected release #{release.version} (HTTP #{response.code})" unless response.is_a?(Net::HTTPSuccess)
    puts "Registered DockFlow #{release.version}"
  end
end

appcast_path = File.expand_path('../appcast.xml', __dir__)
current = parse_releases(File.read(appcast_path), appcast_path)

if (index = ARGV.index('--previous-ref'))
  ref = ARGV[index + 1]
  abort '--previous-ref requires a Git ref' if ref.nil? || ref.empty?
  verify_append_only(current, load_git_appcast(ref))
end

register_releases(current) if ARGV.include?('--register')
puts "Validated #{current.length} append-only DockFlow releases"
