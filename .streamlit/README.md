# Streamlit Cloud Configuration

Contains the Streamlit configuration file for the SecureFlow demo dashboard deployed at `https://secureflowll.streamlit.app/`.

## Files

### config.toml

Streamlit's `[server]` and `[browser]` section configuration:

```toml
[server]
maxUploadSize = 4096
headless = true

[browser]
gatherUsageStats = false
```

**Configuration Details:**

| Setting | Value | Purpose |
|---------|-------|---------|
| `server.maxUploadSize` | `4096` | Sets the maximum file upload size to 4 GB (in MB units). This allows users to upload codebase zip files of up to 4GB for the "Real" mode scan. The app accepts zip archives containing API codebases for static route analysis and zombie detection. |
| `server.headless` | `true` | Runs Streamlit in headless mode (no browser window opens on the server). Required for Streamlit Cloud deployment and containerized environments where no display is available. |
| `browser.gatherUsageStats` | `false` | Disables anonymous usage statistics collection to Streamlit. Compliant with the platform's privacy-first approach to data handling and GDPR data minimization principles. |
