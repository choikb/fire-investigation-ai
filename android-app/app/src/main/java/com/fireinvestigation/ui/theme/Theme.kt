package com.fireinvestigation.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = FireRed,
    onPrimary = Color.White,
    primaryContainer = FireRedDark,
    onPrimaryContainer = Color.White,
    secondary = FireOrange,
    onSecondary = Color.White,
    secondaryContainer = FireOrangeDark,
    onSecondaryContainer = Color.White,
    tertiary = SafetyBlue,
    onTertiary = Color.White,
    tertiaryContainer = SafetyBlue,
    onTertiaryContainer = Color.White,
    error = ErrorRed,
    onError = Color.White,
    errorContainer = ErrorRed,
    onErrorContainer = Color.White,
    background = DarkGray,
    onBackground = Color.White,
    surface = SmokeGray,
    onSurface = Color.White,
    surfaceVariant = AshGray,
    onSurfaceVariant = LightGray,
    outline = MediumGray
)

private val LightColorScheme = lightColorScheme(
    primary = FireRed,
    onPrimary = Color.White,
    primaryContainer = FireRedLight,
    onPrimaryContainer = FireRedDark,
    secondary = FireOrange,
    onSecondary = Color.White,
    secondaryContainer = FireOrangeLight,
    onSecondaryContainer = FireOrangeDark,
    tertiary = SafetyBlue,
    onTertiary = Color.White,
    tertiaryContainer = SafetyBlue.copy(alpha = 0.1f),
    onTertiaryContainer = SafetyBlue,
    error = ErrorRed,
    onError = Color.White,
    errorContainer = ErrorRed.copy(alpha = 0.1f),
    onErrorContainer = ErrorRed,
    background = BackgroundGray,
    onBackground = DarkGray,
    surface = Color.White,
    onSurface = DarkGray,
    surfaceVariant = VeryLightGray,
    onSurfaceVariant = MediumGray,
    outline = LightGray
)

@Composable
fun FireInvestigationTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
