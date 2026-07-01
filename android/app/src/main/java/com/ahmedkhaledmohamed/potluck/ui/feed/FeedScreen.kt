package com.ahmedkhaledmohamed.potluck.ui.feed

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors

@Composable
fun FeedScreen(
    onMealClick: (String) -> Unit,
    viewModel: FeedViewModel = hiltViewModel()
) {
    val meals by viewModel.allMeals.collectAsStateWithLifecycle(initialValue = emptyList())
    val searchText by viewModel.searchText.collectAsStateWithLifecycle()
    var showSearch by remember { mutableStateOf(false) }
    val filtered = viewModel.filteredMeals(meals)

    Column(modifier = Modifier.fillMaxSize()) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                "Potluck",
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Serif,
                color = PotluckColors.text
            )
            Spacer(Modifier.weight(1f))
            IconButton(onClick = { showSearch = !showSearch }) {
                Icon(Icons.Filled.Search, "Search", tint = PotluckColors.textMuted)
            }
        }

        if (showSearch) {
            OutlinedTextField(
                value = searchText,
                onValueChange = { viewModel.setSearchText(it) },
                placeholder = { Text("Search meals or ingredients") },
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp),
                singleLine = true
            )
        }

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(2.dp)
        ) {
            items(filtered, key = { it.id }) { meal ->
                MealCard(meal = meal, onClick = { onMealClick(meal.id) })
            }
        }
    }
}
