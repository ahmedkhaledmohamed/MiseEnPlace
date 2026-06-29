#!/bin/bash
set -e

API_KEY_ID="532Q5RZF4S"
API_ISSUER_ID="b9178d52-7721-4076-b666-61a81aec07a6"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IOS_DIR="$(dirname "$SCRIPT_DIR")"
KEY_PATH="$IOS_DIR/keys/AuthKey_${API_KEY_ID}.p8"
ARCHIVE_PATH="$IOS_DIR/build/MiseEnPlace.xcarchive"
EXPORT_PATH="$IOS_DIR/build/export"
EXPORT_OPTIONS="$IOS_DIR/ExportOptions.plist"

if [ ! -f "$KEY_PATH" ]; then
    echo "Error: API key not found at $KEY_PATH"
    exit 1
fi

echo "=== Uploading Cooknect to TestFlight ==="

echo "→ Generating Xcode project..."
cd "$IOS_DIR"
xcodegen generate 2>&1 | tail -1

echo "→ Archiving..."
rm -rf build/
xcodebuild archive \
    -project MiseEnPlace.xcodeproj \
    -scheme MiseEnPlace \
    -archivePath "$ARCHIVE_PATH" \
    -destination "generic/platform=iOS" \
    -authenticationKeyPath "$KEY_PATH" \
    -authenticationKeyID "$API_KEY_ID" \
    -authenticationKeyIssuerID "$API_ISSUER_ID" \
    -allowProvisioningUpdates \
    CODE_SIGN_STYLE=Automatic \
    2>&1 | tail -3

if [ ! -d "$ARCHIVE_PATH" ]; then
    echo "Error: Archive failed"
    exit 1
fi

echo "→ Exporting and uploading..."
# Use system rsync to avoid Homebrew rsync compatibility issue
PATH="/usr/bin:$PATH" xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_PATH" \
    -exportOptionsPlist "$EXPORT_OPTIONS" \
    -authenticationKeyPath "$KEY_PATH" \
    -authenticationKeyID "$API_KEY_ID" \
    -authenticationKeyIssuerID "$API_ISSUER_ID" \
    -allowProvisioningUpdates \
    2>&1 | tail -5

echo ""
echo "=== Done! Check: https://appstoreconnect.apple.com ==="
