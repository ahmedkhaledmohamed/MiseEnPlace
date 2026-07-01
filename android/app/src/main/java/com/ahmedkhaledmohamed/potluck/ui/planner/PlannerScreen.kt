package com.ahmedkhaledmohamed.potluck.ui.planner
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors
@Composable
fun PlannerScreen() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { Text("Weekly Plan", color = PotluckColors.text) }
}
