package com.fireinvestigation.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.fireinvestigation.data.model.Investigation
import com.fireinvestigation.data.model.InvestigationStatus
import com.fireinvestigation.ui.theme.*

/**
 * 대시보드 화면 - 태블릿 최적화
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    onNavigateToInvestigations: () -> Unit,
    onNavigateToInvestigation: (Int) -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        "🔥 소방 AI 화재조사 시스템",
                        style = MaterialTheme.typography.headlineMedium
                    )
                },
                actions = {
                    IconButton(onClick = { /* 설정 */ }) {
                        Icon(Icons.Default.Settings, "설정")
                    }
                    IconButton(onClick = { /* 로그아웃 */ }) {
                        Icon(Icons.Default.Logout, "로그아웃")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = FireRed,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    actionIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // 통계 카드 행
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                StatCard(
                    title = "총 조사",
                    value = "128",
                    icon = Icons.Default.Assignment,
                    color = FireRed,
                    modifier = Modifier.weight(1f)
                )
                StatCard(
                    title = "이번 달",
                    value = "12",
                    icon = Icons.Default.Today,
                    color = FireOrange,
                    modifier = Modifier.weight(1f)
                )
                StatCard(
                    title = "분석 대기",
                    value = "5",
                    icon = Icons.Default.Pending,
                    color = StatusPending,
                    modifier = Modifier.weight(1f)
                )
                StatCard(
                    title = "완료",
                    value = "98",
                    icon = Icons.Default.CheckCircle,
                    color = SafetyGreen,
                    modifier = Modifier.weight(1f)
                )
            }
            
            // 메인 콘텐츠 영역
            Row(
                modifier = Modifier.fillMaxSize(),
                horizontalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                // 왼쪽: 주요 작업 버튼
                Card(
                    modifier = Modifier
                        .weight(0.4f)
                        .fillMaxHeight(),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            "주요 작업",
                            style = MaterialTheme.typography.headlineSmall
                        )
                        
                        ActionButton(
                            text = "새 조사 시작",
                            icon = Icons.Default.AddCircle,
                            color = FireRed,
                            onClick = onNavigateToInvestigations
                        )
                        
                        ActionButton(
                            text = "조사 목록",
                            icon = Icons.Default.List,
                            color = SafetyBlue,
                            onClick = onNavigateToInvestigations
                        )
                        
                        ActionButton(
                            text = "유사 사례 검색",
                            icon = Icons.Default.Search,
                            color = FireOrange,
                            onClick = {}
                        )
                        
                        ActionButton(
                            text = "AI 챗봇",
                            icon = Icons.Default.Chat,
                            color = SafetyGreen,
                            onClick = {}
                        )
                        
                        Divider(modifier = Modifier.padding(vertical = 8.dp))
                        
                        Text(
                            "동기화 상태",
                            style = MaterialTheme.typography.titleMedium
                        )
                        
                        SyncStatusCard()
                    }
                }
                
                // 오른쪽: 최근 조사
                Card(
                    modifier = Modifier
                        .weight(0.6f)
                        .fillMaxHeight(),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(24.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "최근 조사 사건",
                                style = MaterialTheme.typography.headlineSmall
                            )
                            TextButton(onClick = onNavigateToInvestigations) {
                                Text("전첼 보기")
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        // 최근 사건 목록
                        RecentInvestigationsList(
                            investigations = sampleInvestigations,
                            onItemClick = onNavigateToInvestigation
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun StatCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: androidx.compose.ui.graphics.Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.height(120.dp),
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.1f)),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(32.dp)
            )
            Column {
                Text(
                    text = value,
                    style = MaterialTheme.typography.headlineLarge,
                    color = color
                )
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                )
            }
        }
    }
}

@Composable
private fun ActionButton(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: androidx.compose.ui.graphics.Color,
    onClick: () -> Unit
) {
    ElevatedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        colors = ButtonDefaults.elevatedButtonColors(
            containerColor = color.copy(alpha = 0.1f),
            contentColor = color
        )
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(24.dp))
        Spacer(modifier = Modifier.width(12.dp))
        Text(text, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.weight(1f))
        Icon(Icons.Default.ChevronRight, contentDescription = null)
    }
}

@Composable
private fun SyncStatusCard() {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = SafetyGreen.copy(alpha = 0.1f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                Icons.Default.CloudDone,
                contentDescription = null,
                tint = SafetyGreen
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(
                    "동기화 완료",
                    style = MaterialTheme.typography.bodyMedium,
                    color = SafetyGreen
                )
                Text(
                    "마지막 동기화: 2분 전",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
        }
    }
}

@Composable
private fun RecentInvestigationsList(
    investigations: List<Investigation>,
    onItemClick: (Int) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        investigations.forEach { investigation ->
            InvestigationListItem(
                investigation = investigation,
                onClick = { onItemClick(investigation.id) }
            )
        }
    }
}

@Composable
private fun InvestigationListItem(
    investigation: Investigation,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    investigation.title,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    "${investigation.caseNumber} | ${investigation.address ?: "위치 미상"}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            StatusBadge(status = investigation.status)
        }
    }
}

@Composable
private fun StatusBadge(status: InvestigationStatus) {
    val (text, color) = when (status) {
        InvestigationStatus.PENDING -> "대기" to StatusPending
        InvestigationStatus.IN_PROGRESS -> "진행" to StatusInProgress
        InvestigationStatus.ANALYZING -> "분석" to StatusAnalyzing
        InvestigationStatus.REVIEWING -> "검토" to StatusReviewing
        InvestigationStatus.COMPLETED -> "완료" to StatusCompleted
        InvestigationStatus.ARCHIVED -> "아카이브" to StatusArchived
    }
    
    Surface(
        color = color.copy(alpha = 0.2f),
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            color = color,
            style = MaterialTheme.typography.labelMedium
        )
    }
}

// 샘플 데이터
private val sampleInvestigations = listOf(
    Investigation(
        id = 1,
        caseNumber = "FIRE-2024-001A",
        title = "주방 화재 조사",
        description = "전열기 과열로 인한 화재",
        address = "서울시 강남구 테헤란로 123",
        status = InvestigationStatus.COMPLETED,
        investigatorId = 1,
        createdAt = java.util.Date(),
        isReportApproved = true,
        isSynced = true
    ),
    Investigation(
        id = 2,
        caseNumber = "FIRE-2024-001B",
        title = "전력실 화재",
        description = "변압기 합선 추정",
        address = "서울시 송파구 오금로 456",
        status = InvestigationStatus.ANALYZING,
        investigatorId = 1,
        createdAt = java.util.Date(),
        isReportApproved = false,
        isSynced = true
    ),
    Investigation(
        id = 3,
        caseNumber = "FIRE-2024-001C",
        title = "상가 화재",
        description = "원인 미상",
        address = "서울시 마포구 홍익로 789",
        status = InvestigationStatus.IN_PROGRESS,
        investigatorId = 1,
        createdAt = java.util.Date(),
        isReportApproved = false,
        isSynced = true
    )
)
