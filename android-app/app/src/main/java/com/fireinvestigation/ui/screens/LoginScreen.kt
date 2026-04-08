package com.fireinvestigation.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.fireinvestigation.ui.theme.FireRed

/**
 * 로그인 화면
 */
@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit
) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(48.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // 로고
        Icon(
            Icons.Default.LocalFireDepartment,
            contentDescription = "로고",
            modifier = Modifier.size(120.dp),
            tint = FireRed
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            "소방 AI 화재조사 시스템",
            style = MaterialTheme.typography.headlineLarge,
            textAlign = TextAlign.Center
        )
        
        Text(
            "Fire Investigation AI",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
        )
        
        Spacer(modifier = Modifier.height(48.dp))
        
        // 로그인 폼
        Card(
            modifier = Modifier.width(400.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(32.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    "로그인",
                    style = MaterialTheme.typography.headlineSmall
                )
                
                // 사용자명
                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it },
                    label = { Text("사용자명 / 배지번호") },
                    leadingIcon = { Icon(Icons.Default.Person, null) },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Text,
                        imeAction = ImeAction.Next
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
                
                // 비밀번호
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = { Text("비밀번호") },
                    leadingIcon = { Icon(Icons.Default.Lock, null) },
                    singleLine = true,
                    visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Password,
                        imeAction = ImeAction.Done
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
                
                // 오류 메시지
                if (errorMessage != null) {
                    Text(
                        errorMessage!!,
                        color = MaterialTheme.colorScheme.error,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // 로그인 버튼
                Button(
                    onClick = {
                        isLoading = true
                        // TODO: 실제 로그인 API 호출
                        // 임시: 바로 로그인 성공
                        isLoading = false
                        onLoginSuccess()
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isLoading && username.isNotBlank() && password.isNotBlank()
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Text("로그인", style = MaterialTheme.typography.bodyLarge)
                    }
                }
                
                // 오프라인 모드
                TextButton(
                    onClick = { /* 오프라인 모드 */ },
                    modifier = Modifier.align(Alignment.CenterHorizontally)
                ) {
                    Text("오프라인 모드로 작업")
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Text(
            "© 2024 소방청 AI 디지털 지원체계",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
        )
    }
}
