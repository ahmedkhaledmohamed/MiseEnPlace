#!/bin/bash
set -e

API_KEY_ID="532Q5RZF4S"
API_ISSUER_ID="b9178d52-7721-4076-b666-61a81aec07a6"
BUNDLE_ID="com.ahmedkhaledmohamed.MiseEnPlace"

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

# --- Generate JWT for ASC API ---
generate_jwt() {
    local header=$(printf '{"alg":"ES256","kid":"%s","typ":"JWT"}' "$API_KEY_ID" | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')
    local now=$(date +%s)
    local exp=$((now + 1200))
    local payload=$(printf '{"iss":"%s","iat":%d,"exp":%d,"aud":"appstoreconnect-v1"}' "$API_ISSUER_ID" "$now" "$exp" | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')
    local unsigned="${header}.${payload}"
    local signature=$(printf '%s' "$unsigned" | openssl dgst -sha256 -sign "$KEY_PATH" | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')
    echo "${unsigned}.${signature}"
}

echo "=== Uploading Potluck to TestFlight ==="

# Step 1: Generate project
echo "→ Generating Xcode project..."
cd "$IOS_DIR"
xcodegen generate 2>&1 | tail -1

# Step 2: Archive
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

# Step 3: Export and upload
echo "→ Exporting and uploading..."
PATH="/usr/bin:$PATH" xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_PATH" \
    -exportOptionsPlist "$EXPORT_OPTIONS" \
    -authenticationKeyPath "$KEY_PATH" \
    -authenticationKeyID "$API_KEY_ID" \
    -authenticationKeyIssuerID "$API_ISSUER_ID" \
    -allowProvisioningUpdates \
    2>&1 | tail -5

# Step 4: Wait for processing and enable internal testing
echo "→ Enabling internal testing..."
JWT=$(generate_jwt)

# Get the app ID
APP_ID=$(curl -s -H "Authorization: Bearer $JWT" \
    "https://api.appstoreconnect.apple.com/v1/apps?filter[bundleId]=$BUNDLE_ID" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null)

if [ -z "$APP_ID" ]; then
    echo "Warning: Could not find app ID. Enable internal testing manually."
else
    echo "  App ID: $APP_ID"

    # Get or create internal beta group
    GROUP_ID=$(curl -s -H "Authorization: Bearer $JWT" \
        "https://api.appstoreconnect.apple.com/v1/apps/$APP_ID/betaGroups?filter[isInternalGroup]=true" \
        | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(d[0]['id'] if d else '')" 2>/dev/null)

    if [ -z "$GROUP_ID" ]; then
        echo "  No internal test group found. Creating one..."
        GROUP_ID=$(curl -s -X POST -H "Authorization: Bearer $JWT" \
            -H "Content-Type: application/json" \
            -d "{\"data\":{\"type\":\"betaGroups\",\"attributes\":{\"name\":\"Internal Testers\",\"isInternalGroup\":true},\"relationships\":{\"app\":{\"data\":{\"type\":\"apps\",\"id\":\"$APP_ID\"}}}}}" \
            "https://api.appstoreconnect.apple.com/v1/betaGroups" \
            | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
    fi
    echo "  Beta group: $GROUP_ID"

    # Wait for build to appear (up to 2 min)
    echo "  Waiting for build to process..."
    for i in $(seq 1 12); do
        BUILD_ID=$(curl -s -H "Authorization: Bearer $JWT" \
            "https://api.appstoreconnect.apple.com/v1/apps/$APP_ID/builds?sort=-uploadedDate&limit=1" \
            | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(d[0]['id'] if d else '')" 2>/dev/null)

        if [ -n "$BUILD_ID" ]; then
            BUILD_STATE=$(curl -s -H "Authorization: Bearer $JWT" \
                "https://api.appstoreconnect.apple.com/v1/builds/$BUILD_ID" \
                | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['attributes'].get('processingState',''))" 2>/dev/null)

            if [ "$BUILD_STATE" = "VALID" ]; then
                echo "  Build $BUILD_ID is valid. Adding to internal testers..."
                curl -s -X POST -H "Authorization: Bearer $JWT" \
                    -H "Content-Type: application/json" \
                    -d "{\"data\":[{\"type\":\"builds\",\"id\":\"$BUILD_ID\"}]}" \
                    "https://api.appstoreconnect.apple.com/v1/betaGroups/$GROUP_ID/relationships/builds" > /dev/null
                echo "  ✓ Internal testers will be notified automatically"
                break
            fi
            echo "  Build state: $BUILD_STATE (attempt $i/12)..."
        fi
        sleep 10
    done

    if [ -z "$BUILD_ID" ] || [ "$BUILD_STATE" != "VALID" ]; then
        echo "  Build still processing. Internal testers will need to be added manually."
    fi
fi

echo ""
echo "=== Done! Check: https://appstoreconnect.apple.com ==="
