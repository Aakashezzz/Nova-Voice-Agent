# Google Drive Submission Guide

Steps to package and submit this project via Google Drive.

## 1. Prepare the archive

From the project root:

```bash
zip -r voice-assistant-submission.zip . \
  -x "**/node_modules/*" "**/.venv/*" "**/__pycache__/*" "**/dist/*" "**/*.onnx" "**/*.onnx.json"
```

This excludes large/regeneratable artifacts (dependencies, model weights,
build output) so the archive stays small and reviewable. Model download
instructions are in `docs/INSTALLATION.md` so reviewers can fetch them
independently.

## 2. Upload to Google Drive

1. Go to [drive.google.com](https://drive.google.com) and sign in.
2. Create a folder named `[YourName]-VoiceAssistant-Internship`.
3. Upload `voice-assistant-submission.zip` into that folder.
4. Also upload the standalone PDF report (`docs/SUBMISSION_REPORT.pdf`) directly into the folder for quick reviewer access without unzipping.

## 3. Set sharing permissions

1. Right-click the folder → **Share**.
2. Under "General access," change to **"Anyone with the link"** → **Viewer**.
3. Copy the shareable link.

## 4. Submission checklist

- [ ] `voice-assistant-submission.zip` uploaded
- [ ] `SUBMISSION_REPORT.pdf` uploaded separately
- [ ] Folder sharing set to "Anyone with the link – Viewer"
- [ ] Link tested in an incognito/private browser window to confirm access works without sign-in
- [ ] Link submitted through your internship's designated submission form/channel

## Google Drive Links Placeholder

| Item | Link |
|------|------|
| Project folder | `[PASTE SHAREABLE FOLDER LINK HERE]` |
| Submission ZIP | `[PASTE FILE LINK HERE]` |
| PDF report | `[PASTE FILE LINK HERE]` |
