package com.ahmedkhaledmohamed.potluck.ui.favorites

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ahmedkhaledmohamed.potluck.ui.feed.MealCard
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors

@Composable
fun FavoritesScreen(
    onMealClick: (String) -> Unit = {},
    viewModel: FavoritesViewModel = hiltViewModel()
) {
    val meals by viewModel.allMeals.collectAsStateWithLifecycle(initialValue = emptyList())
    val favs by viewModel.favorites.collectAsStateWithLifecycle(initialValue = emptyList())
    val favMeals = viewModel.favoriteMeals(meals, favs)

    Column(modifier = Modifier.fillMaxSize()) {
        Text("Favorites", fontSize = 28.sp, color = PotluckColors.text,
            modifier = Modifier.padding(16.dp))

        if (favMeals.isEmpty()) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(Icons.Outlined.FavoriteBorder, null, tint = PotluckColors.textMuted,
                        modifier = Modifier.size(48.dp))
                    Spacer(Modifier.height(12.dp))
                    Text("No favorites yet", color = PotluckColors.text)
                    Text("Heart meals you love to find them here", color = PotluckColors.textMuted, fontSize = 14.sp)
                }
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                items(favMeals, key = { it.id }) { meal ->
                    MealCard(meal = meal, onClick = { onMealClick(meal.id) })
                }
            }
        }
    }
}
