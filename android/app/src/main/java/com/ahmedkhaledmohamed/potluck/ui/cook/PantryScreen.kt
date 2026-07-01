package com.ahmedkhaledmohamed.potluck.ui.cook

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.ahmedkhaledmohamed.potluck.data.db.MealEntity
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors

@Composable
fun PantryScreen(
    onMealClick: (String) -> Unit = {},
    viewModel: PantryViewModel = hiltViewModel()
) {
    val meals by viewModel.allMeals.collectAsStateWithLifecycle(initialValue = emptyList())
    val selected by viewModel.selected.collectAsStateWithLifecycle()
    val search by viewModel.search.collectAsStateWithLifecycle()

    val allIngs = remember(meals) {
        val map = mutableMapOf<String, Pair<String, Int>>()
        meals.forEach { meal ->
            meal.dietaryTags // trigger access
        }
        map.entries.map { IngredientInfo(it.key, it.value.first, it.value.second) }
            .sortedByDescending { it.count }
    }

    val matches = remember(meals, selected) {
        if (selected.isEmpty()) emptyList()
        else meals.mapNotNull { meal ->
            val matched = selected.size // simplified for placeholder
            if (matched > 0) MealMatch(meal, matched, 8, emptyList()) else null
        }.sortedByDescending { it.matched.toDouble() / it.total }
            .take(30)
    }

    Column(modifier = Modifier.fillMaxSize()) {
        Row(modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)) {
            Text("What can I cook?", fontSize = 24.sp, fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Serif, color = PotluckColors.text)
            Spacer(Modifier.weight(1f))
            if (selected.isNotEmpty()) {
                TextButton(onClick = { viewModel.clear() }) {
                    Text("Clear", color = PotluckColors.accent)
                }
            }
        }

        OutlinedTextField(
            value = search, onValueChange = { viewModel.setSearch(it) },
            placeholder = { Text("Search ingredients...") },
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
            singleLine = true
        )

        Spacer(Modifier.height(8.dp))

        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("Coming soon — ingredient picker", color = PotluckColors.textMuted)
        }
    }
}
