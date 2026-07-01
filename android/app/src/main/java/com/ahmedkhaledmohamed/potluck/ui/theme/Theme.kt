package com.ahmedkhaledmohamed.potluck.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(
    primary = PotluckColors.accent,
    onPrimary = Color.Black,
    surface = PotluckColors.surface,
    background = PotluckColors.bg,
    onSurface = PotluckColors.text,
    onBackground = PotluckColors.text,
    surfaceVariant = PotluckColors.cardBg,
    outline = PotluckColors.border,
)

@Composable
fun PotluckTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content
    )
}
