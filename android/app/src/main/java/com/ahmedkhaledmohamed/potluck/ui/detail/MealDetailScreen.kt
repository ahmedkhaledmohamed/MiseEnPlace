package com.ahmedkhaledmohamed.potluck.ui.detail

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.ahmedkhaledmohamed.potluck.ui.components.MealActions
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MealDetailScreen(
    mealId: String,
    onBack: () -> Unit,
    viewModel: MealDetailViewModel = hiltViewModel()
) {
    val meal by viewModel.meal.collectAsStateWithLifecycle(initialValue = null)
    val ingredients by viewModel.ingredients.collectAsStateWithLifecycle(initialValue = emptyList())
    val steps by viewModel.steps.collectAsStateWithLifecycle(initialValue = emptyList())
    val isFavorited by viewModel.isFavorited.collectAsStateWithLifecycle(initialValue = false)

    meal?.let { m ->
        Scaffold(
            topBar = {
                TopAppBar(
                    title = {},
                    navigationIcon = {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = PotluckColors.text)
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = PotluckColors.bg)
                )
            },
            containerColor = PotluckColors.bg
        ) { padding ->
            LazyColumn(
                modifier = Modifier.padding(padding).fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                item {
                    AsyncImage(
                        model = m.imageUrl, contentDescription = m.name,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.fillMaxWidth().height(380.dp)
                    )
                }

                item {
                    MealActions(
                        meal = m, isFavorited = isFavorited,
                        onToggleFavorite = { viewModel.toggleFavorite() },
                        onAddToPlan = {},
                        modifier = Modifier.padding(horizontal = 16.dp)
                    )
                }

                item {
                    Column(modifier = Modifier.padding(horizontal = 16.dp)) {
                        Text(m.cuisine, fontSize = 12.sp, fontWeight = FontWeight.Bold,
                            color = PotluckColors.cuisineColor(m.cuisine),
                            modifier = Modifier.background(
                                PotluckColors.cuisineColor(m.cuisine).copy(alpha = 0.15f),
                                RoundedCornerShape(50)
                            ).padding(horizontal = 10.dp, vertical = 4.dp))
                        Spacer(Modifier.height(6.dp))
                        Text(m.name, fontSize = 24.sp, fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Serif, color = PotluckColors.text)
                        Spacer(Modifier.height(4.dp))
                        Text(m.description, fontSize = 14.sp, color = PotluckColors.textMuted)
                    }
                }

                item {
                    Row(modifier = Modifier.padding(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        StatCard("Time", "${m.totalTime} min", Modifier.weight(1f))
                        StatCard("Cost", "${"$%.2f".format(m.costPerServing)}", Modifier.weight(1f))
                        StatCard("Servings", "${m.servings}", Modifier.weight(1f))
                    }
                }

                if (m.dietaryTags.isNotEmpty()) {
                    item {
                        LazyRow(contentPadding = PaddingValues(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            items(m.dietaryTags) { tag ->
                                Text(tag, fontSize = 12.sp, color = PotluckColors.green,
                                    modifier = Modifier.background(PotluckColors.green.copy(alpha = 0.15f), RoundedCornerShape(50))
                                        .padding(horizontal = 10.dp, vertical = 4.dp))
                            }
                        }
                    }
                }

                item { SectionHeader("Ingredients", Modifier.padding(horizontal = 16.dp)) }
                items(ingredients.sortedBy { it.name }) { ing ->
                    Row(modifier = Modifier.padding(horizontal = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(8.dp).clip(CircleShape).background(PotluckColors.categoryColor(ing.category)))
                        Spacer(Modifier.width(8.dp))
                        Text(ing.name, fontSize = 14.sp, color = if (ing.isOptional) PotluckColors.textMuted else PotluckColors.text,
                            fontStyle = if (ing.isOptional) FontStyle.Italic else FontStyle.Normal, modifier = Modifier.weight(1f))
                        Text("${ing.quantity} ${ing.unit}", fontSize = 12.sp, color = PotluckColors.textMuted)
                    }
                }

                item { SectionHeader("Steps", Modifier.padding(horizontal = 16.dp)) }
                items(steps.sortedBy { it.order }) { step ->
                    Row(modifier = Modifier.padding(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text("${step.order}", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = PotluckColors.accent)
                        Text(step.instruction, fontSize = 14.sp, color = PotluckColors.text)
                    }
                }

                if (m.tips.isNotEmpty()) {
                    item { SectionHeader("Tips", Modifier.padding(horizontal = 16.dp)) }
                    items(m.tips) { tip ->
                        Text("• $tip", fontSize = 14.sp, color = PotluckColors.textMuted,
                            modifier = Modifier.padding(horizontal = 16.dp))
                    }
                }

                item { Spacer(Modifier.height(20.dp)) }
            }
        }
    }
}

@Composable
private fun StatCard(label: String, value: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.background(PotluckColors.surface, RoundedCornerShape(8.dp)).padding(vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(label, fontSize = 12.sp, color = PotluckColors.textMuted)
        Text(value, fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = PotluckColors.text)
    }
}

@Composable
private fun SectionHeader(title: String, modifier: Modifier = Modifier) {
    Text(title.uppercase(), fontSize = 12.sp, fontWeight = FontWeight.SemiBold,
        color = PotluckColors.textMuted, letterSpacing = 1.sp, modifier = modifier.padding(top = 8.dp))
}
