# Logging & Monitoring

## Logging

- All requests are logged via `request_logger.rs`
- Logs are written to `backend.log`

## Monitoring

- Regularly check logs for errors or suspicious activity
- Consider integrating with external monitoring tools for production

## Troubleshooting

- Check `backend.log` for errors
- Use `RUST_LOG=debug` for more verbose output