# dock-flow-updates

Visit the official website at https://dockflow.appitstudio.com

## Release history contract

`appcast.xml` is an append-only ledger as well as DockFlow's production Sparkle feed. Never remove or rewrite a published item: users with a one-year update window may need Sparkle to select the newest historical release they are entitled to install. Every retained item must include an RFC 2822 `pubDate`, immutable versioned HTTPS enclosure URL, positive byte length, and Ed25519 signature.

The reconstructed history currently starts at 1.59. Those items were recovered only where both repository history and an immutable GitHub Release supplied trustworthy version, asset, signature, and publication metadata. Versions 1.58 and earlier were deliberately not reconstructed because the available evidence was ambiguous or referenced a mutable `prod` asset; dates must never be guessed or backdated.

Run the same validation used by CI before publishing:

```bash
ruby scripts/appcast_releases.rb --previous-ref origin/main
```

## Keyper registration

On a push to `main`, `.github/workflows/appcast-releases.yml` validates the feed and idempotently registers every retained item with Keyper. Configure the repository Actions secret `KEYPER_RELEASE_TOKEN` with the dedicated server-only release-write token for DockFlow's `stable` release track. This is not the client validation credential and must never be added to the app, feed, logs, or repository.

The token selects the product and release track. If a future item uses a Sparkle beta channel, it is still registered by this same workflow and same DockFlow feed token; Sparkle channel names do not select Keyper credentials.
