package com.ahmedkhaledmohamed.potluck.ui.planner

import androidx.compose.foundation.layout.*
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
fun PlannerScreen() {
    Column(modifier = Modifier.fillMaxSize()) {
        Text("Weekly Plan", fontSize = 28.sp, fontWeight = FontWeight.Bold,
            fontFamily = FontFamily.Serif, color = PotluckColors.text,
            modifier = Modifier.padding(16.dp))

        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("Coming soon — weekly planner", color = PotluckColors.textMuted)
        }
    }
}
