package com.ahmedkhaledmohamed.potluck.ui.favorites
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors
@Composable
fun FavoritesScreen(onMealClick: (String) -> Unit = {}) {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { Text("Favorites", color = PotluckColors.text) }
}
