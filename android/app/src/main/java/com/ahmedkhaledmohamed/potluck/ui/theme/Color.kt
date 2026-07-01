package com.ahmedkhaledmohamed.potluck.ui.theme

import androidx.compose.ui.graphics.Color

object PotluckColors {
    val bg = Color(0xFF0F1117)
    val surface = Color(0xFF1A1D27)
    val cardBg = Color(0xFF1E2130)
    val border = Color(0xFF2A2D3A)
    val text = Color(0xFFE4E4E7)
    val textMuted = Color(0xFF71717A)
    val accent = Color(0xFFF59E0B)
    val green = Color(0xFF22C55E)
    val red = Color(0xFFEF4444)

    val cuisineColors = mapOf(
        "Chinese" to Color(0xFFEF4444), "Japanese" to Color(0xFFF87171),
        "Korean" to Color(0xFFDC2626), "East Asian" to Color(0xFFFB923C),
        "Thai" to Color(0xFFF97316), "Vietnamese" to Color(0xFFEA580C),
        "Southeast Asian" to Color(0xFFFB923C), "Indian" to Color(0xFFEAB308),
        "South Asian" to Color(0xFFFACC15), "Middle Eastern" to Color(0xFF22C55E),
        "Turkish" to Color(0xFF16A34A), "Greek" to Color(0xFF4ADE80),
        "Mediterranean" to Color(0xFF34D399), "French" to Color(0xFF3B82F6),
        "Italian" to Color(0xFF60A5FA), "Spanish" to Color(0xFF2563EB),
        "British" to Color(0xFF93C5FD), "Scandinavian" to Color(0xFF7DD3FC),
        "Eastern European" to Color(0xFF818CF8), "American" to Color(0xFFA78BFA),
        "Mexican" to Color(0xFFC084FC), "Latin American" to Color(0xFFD946EF),
        "Caribbean" to Color(0xFFE879F9), "African" to Color(0xFFF472B6),
        "Fusion" to Color(0xFF94A3B8),
    )

    val categoryColors = mapOf(
        "protein" to Color(0xFFEF4444), "vegetable" to Color(0xFF22C55E),
        "fruit" to Color(0xFFF97316), "grain" to Color(0xFFEAB308),
        "dairy" to Color(0xFF93C5FD), "spice" to Color(0xFFF59E0B),
        "oil-fat" to Color(0xFFA3A3A3), "sauce-condiment" to Color(0xFFC084FC),
        "herb" to Color(0xFF34D399), "legume" to Color(0xFFA78BFA),
        "nut-seed" to Color(0xFFD97706), "sweetener" to Color(0xFFF472B6),
        "liquid" to Color(0xFF7DD3FC), "other" to Color(0xFF64748B),
    )

    fun cuisineColor(cuisine: String) = cuisineColors[cuisine] ?: Color(0xFF94A3B8)
    fun categoryColor(category: String) = categoryColors[category] ?: Color(0xFF64748B)
}
