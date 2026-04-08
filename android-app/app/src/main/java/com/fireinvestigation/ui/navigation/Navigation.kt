package com.fireinvestigation.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.fireinvestigation.ui.screens.*

/**
 * 네비게이션 설정
 */
object Routes {
    const val LOGIN = "login"
    const val DASHBOARD = "dashboard"
    const val INVESTIGATION_LIST = "investigations"
    const val INVESTIGATION_DETAIL = "investigation/{id}"
    const val CREATE_INVESTIGATION = "investigation/create"
    const val CAMERA = "camera/{investigationId}"
    const val ANALYSIS_RESULT = "analysis/{investigationId}/{evidenceId}"
    const val REPORT = "report/{investigationId}"
    const val CHAT = "chat/{investigationId}"
    
    fun investigationDetail(id: Int) = "investigation/$id"
    fun camera(investigationId: Int) = "camera/$investigationId"
    fun analysisResult(investigationId: Int, evidenceId: Int) = "analysis/$investigationId/$evidenceId"
    fun report(investigationId: Int) = "report/$investigationId"
    fun chat(investigationId: Int) = "chat/$investigationId"
}

@Composable
fun FireNavHost(
    navController: NavHostController = rememberNavController(),
    startDestination: String = Routes.LOGIN
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Routes.LOGIN) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Routes.DASHBOARD) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Routes.DASHBOARD) {
            DashboardScreen(
                onNavigateToInvestigations = {
                    navController.navigate(Routes.INVESTIGATION_LIST)
                },
                onNavigateToInvestigation = { id ->
                    navController.navigate(Routes.investigationDetail(id))
                }
            )
        }
        
        composable(Routes.INVESTIGATION_LIST) {
            InvestigationListScreen(
                onNavigateToDetail = { id ->
                    navController.navigate(Routes.investigationDetail(id))
                },
                onCreateNew = {
                    navController.navigate(Routes.CREATE_INVESTIGATION)
                },
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(Routes.CREATE_INVESTIGATION) {
            CreateInvestigationScreen(
                onInvestigationCreated = { id ->
                    navController.navigate(Routes.investigationDetail(id)) {
                        popUpTo(Routes.INVESTIGATION_LIST)
                    }
                },
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(
            route = Routes.INVESTIGATION_DETAIL,
            arguments = listOf(navArgument("id") { type = NavType.IntType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getInt("id") ?: 0
            InvestigationDetailScreen(
                investigationId = id,
                onNavigateToCamera = {
                    navController.navigate(Routes.camera(id))
                },
                onNavigateToAnalysis = { evidenceId ->
                    navController.navigate(Routes.analysisResult(id, evidenceId))
                },
                onNavigateToReport = {
                    navController.navigate(Routes.report(id))
                },
                onNavigateToChat = {
                    navController.navigate(Routes.chat(id))
                },
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(
            route = Routes.CAMERA,
            arguments = listOf(navArgument("investigationId") { type = NavType.IntType })
        ) { backStackEntry ->
            val investigationId = backStackEntry.arguments?.getInt("investigationId") ?: 0
            CameraScreen(
                investigationId = investigationId,
                onPhotoTaken = { evidenceId ->
                    navController.navigate(Routes.analysisResult(investigationId, evidenceId))
                },
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(
            route = Routes.ANALYSIS_RESULT,
            arguments = listOf(
                navArgument("investigationId") { type = NavType.IntType },
                navArgument("evidenceId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val investigationId = backStackEntry.arguments?.getInt("investigationId") ?: 0
            val evidenceId = backStackEntry.arguments?.getInt("evidenceId") ?: 0
            AnalysisResultScreen(
                investigationId = investigationId,
                evidenceId = evidenceId,
                onNavigateToReport = {
                    navController.navigate(Routes.report(investigationId))
                },
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(
            route = Routes.REPORT,
            arguments = listOf(navArgument("investigationId") { type = NavType.IntType })
        ) { backStackEntry ->
            val investigationId = backStackEntry.arguments?.getInt("investigationId") ?: 0
            ReportScreen(
                investigationId = investigationId,
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(
            route = Routes.CHAT,
            arguments = listOf(navArgument("investigationId") { type = NavType.IntType })
        ) { backStackEntry ->
            val investigationId = backStackEntry.arguments?.getInt("investigationId") ?: 0
            ChatScreen(
                investigationId = investigationId,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
