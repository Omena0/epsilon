
# Epsilon launcher

Very tiny launcher. I might make this a full app someday.

But for now this is just a tiny gui launcher.

The codebase is pretty nice though so its easy to add features to.

## Security

Uses OS keyring to store login data securely.

Uses secure oauth flow.

## Debugging

Basically every function should have a log.trace().
To turn on trace logging do Logger.level = LogLevel.TRACE

### Logging to a file

```py
Logger('channel', files=[sys.stdout, open("logs/file.log")], err_files=[sys.stderr, open("logs/file.log")])
```

Will log to all writable objects in files and err_files for errors and above.
