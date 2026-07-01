package com.ahmedkhaledmohamed.potluck

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import com.ahmedkhaledmohamed.potluck.data.DataSeeder
import com.ahmedkhaledmohamed.potluck.ui.navigation.PotluckNavHost
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckColors
import com.ahmedkhaledmohamed.potluck.ui.theme.PotluckTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    @Inject lateinit var dataSeeder: DataSeeder

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            LaunchedEffect(Unit) { dataSeeder.seedIfNeeded() }

            PotluckTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = PotluckColors.bg
                ) {
                    PotluckNavHost()
                }
            }
        }
    }
}
