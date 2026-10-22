# Logging & Monitoring

## Logging

- Actix logs request metadata; internal Python errors are logged without returning them to clients.
- Logs go to service stderr (systemd journal or rotated Docker logs), not `backend.log`.

## Monitoring

- Regularly check logs for errors or suspicious activity
- Consider integrating with external monitoring tools for production

## Troubleshooting

- Check `journalctl -u cricket-ready-backend.service` or `docker compose logs api` for errors
- Use `RUST_LOG=debug` for more verbose output
