package com.ahmedkhaledmohamed.potluck.ui.grocery

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ShoppingCart
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors

@Composable
fun GroceryScreen() {
    Column(modifier = Modifier.fillMaxSize()) {
        Text("Grocery List", fontSize = 28.sp, fontWeight = FontWeight.Bold,
            fontFamily = FontFamily.Serif, color = PotluckColors.text,
            modifier = Modifier.padding(16.dp))

        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(Icons.Outlined.ShoppingCart, null, tint = PotluckColors.textMuted,
                    modifier = Modifier.size(48.dp))
                Spacer(Modifier.height(12.dp))
                Text("Plan meals first", color = PotluckColors.text, fontWeight = FontWeight.Medium)
                Text("Add meals to your weekly plan to generate a grocery list",
                    color = PotluckColors.textMuted, fontSize = 14.sp)
            }
        }
    }
}
