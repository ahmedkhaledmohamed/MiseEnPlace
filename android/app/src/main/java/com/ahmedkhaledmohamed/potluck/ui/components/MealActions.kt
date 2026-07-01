package com.ahmedkhaledmohamed.potluck.ui.components

import android.content.Context
import android.content.Intent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.ahmedkhaledmohamed.potluck.data.db.FavoriteMealEntity
import com.ahmedkhaledmohamed.potluck.data.db.MealEntity
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors

@Composable
fun MealActions(
    meal: MealEntity,
    isFavorited: Boolean,
    onToggleFavorite: () -> Unit,
    onAddToPlan: () -> Unit,
    modifier: Modifier = Modifier,
    iconSize: Float = 24f
) {
    val context = LocalContext.current

    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        IconButton(onClick = onToggleFavorite, modifier = Modifier.size(44.dp)) {
            Icon(
                if (isFavorited) Icons.Filled.Favorite else Icons.Outlined.FavoriteBorder,
                contentDescription = "Favorite",
                tint = if (isFavorited) PotluckColors.red else PotluckColors.text
            )
        }

        IconButton(onClick = onAddToPlan, modifier = Modifier.size(44.dp)) {
            Icon(Icons.Outlined.CalendarMonth, "Add to plan", tint = PotluckColors.text)
        }

        IconButton(onClick = { shareMeal(context, meal) }, modifier = Modifier.size(44.dp)) {
            Icon(Icons.Outlined.Send, "Share", tint = PotluckColors.text)
        }

        Spacer(Modifier.weight(1f))

        IconButton(onClick = onToggleFavorite, modifier = Modifier.size(44.dp)) {
            Icon(
                if (isFavorited) Icons.Filled.Bookmark else Icons.Outlined.BookmarkBorder,
                contentDescription = "Save",
                tint = if (isFavorited) PotluckColors.accent else PotluckColors.text
            )
        }
    }
}

private fun shareMeal(context: Context, meal: MealEntity) {
    val text = buildString {
        append("${meal.name} — ${meal.cuisine}\n")
        append("${meal.description}\n")
        append("${meal.totalTime} min · ${"$%.2f".format(meal.costPerServing)}/serving")
        meal.imageUrl?.let { append("\n$it") }
    }
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
    }
    context.startActivity(Intent.createChooser(intent, "Share recipe"))
}
