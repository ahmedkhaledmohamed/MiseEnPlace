package com.ahmedkhaledmohamed.potluck.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.*
import com.ahmedkhaledmohamed.potluck.ui.feed.FeedScreen
import com.ahmedkhaledmohamed.potluck.ui.cook.PantryScreen
import com.ahmedkhaledmohamed.potluck.ui.favorites.FavoritesScreen
import com.ahmedkhaledmohamed.potluck.ui.planner.PlannerScreen
import com.ahmedkhaledmohamed.potluck.ui.grocery.GroceryScreen
import com.ahmedkhaledmohamed.potluck.ui.detail.MealDetailScreen
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors

data class BottomNavItem(val route: String, val label: String, val icon: ImageVector)

val bottomNavItems = listOf(
    BottomNavItem("feed", "Feed", Icons.Filled.Home),
    BottomNavItem("cook", "Cook", Icons.Filled.Restaurant),
    BottomNavItem("saved", "Saved", Icons.Filled.Favorite),
    BottomNavItem("plan", "Plan", Icons.Filled.CalendarMonth),
    BottomNavItem("shop", "Shop", Icons.Filled.ShoppingCart),
)

@Composable
fun PotluckNavHost() {
    val navController = rememberNavController()
    val currentBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = currentBackStackEntry?.destination?.route

    Scaffold(
        containerColor = PotluckColors.bg,
        bottomBar = {
            if (currentRoute in bottomNavItems.map { it.route }) {
                NavigationBar(containerColor = PotluckColors.surface) {
                    bottomNavItems.forEach { item ->
                        NavigationBarItem(
                            selected = currentRoute == item.route,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = { Icon(item.icon, contentDescription = item.label) },
                            label = { Text(item.label) },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = PotluckColors.accent,
                                selectedTextColor = PotluckColors.accent,
                                unselectedIconColor = PotluckColors.textMuted,
                                unselectedTextColor = PotluckColors.textMuted,
                                indicatorColor = PotluckColors.accent.copy(alpha = 0.15f),
                            )
                        )
                    }
                }
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = "feed",
            modifier = Modifier.padding(padding)
        ) {
            composable("feed") {
                FeedScreen(onMealClick = { navController.navigate("meal/$it") })
            }
            composable("cook") {
                PantryScreen(onMealClick = { navController.navigate("meal/$it") })
            }
            composable("saved") {
                FavoritesScreen(onMealClick = { navController.navigate("meal/$it") })
            }
            composable("plan") { PlannerScreen() }
            composable("shop") { GroceryScreen() }
            composable("meal/{mealId}") { backStackEntry ->
                val mealId = backStackEntry.arguments?.getString("mealId") ?: return@composable
                MealDetailScreen(mealId = mealId, onBack = { navController.popBackStack() })
            }
        }
    }
}
