package com.fireinvestigation.ui.screens

import android.content.Context
import android.net.Uri
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.fireinvestigation.ui.theme.FireRed
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * 침라 촬영 화면 - Circle-to-Search 기능 포함
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CameraScreen(
    investigationId: Int,
    onPhotoTaken: (Int) -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    
    var imageCapture: ImageCapture? by remember { mutableStateOf(null) }
    var circleCenter by remember { mutableStateOf<Offset?>(null) }
    var circleRadius by remember { mutableStateOf(100f) }
    var isCircleMode by remember { mutableStateOf(false) }
    
    val executor = remember { Executors.newSingleThreadExecutor() }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("증거 촬영") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, "뒤로")
                    }
                },
                actions = {
                    // Circle-to-Search 모드 토글
                    IconButton(onClick = { isCircleMode = !isCircleMode }) {
                        Icon(
                            if (isCircleMode) Icons.Default.Circle else Icons.Default.RadioButtonUnchecked,
                            "영역 선택",
                            tint = if (isCircleMode) FireRed else LocalContentColor.current
                        )
                    }
                    IconButton(onClick = { /* 플래시 */ }) {
                        Icon(Icons.Default.FlashOn, "플래시")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // 침라 프리뷰
            CameraPreview(
                context = context,
                lifecycleOwner = lifecycleOwner,
                onImageCapture = { imageCapture = it }
            )
            
            // Circle-to-Search 오버레이
            if (isCircleMode) {
                CircleToSearchOverlay(
                    circleCenter = circleCenter,
                    circleRadius = circleRadius,
                    onCircleChange = { center, radius ->
                        circleCenter = center
                        circleRadius = radius
                    },
                    modifier = Modifier.fillMaxSize()
                )
                
                // 선택 영역 정보
                if (circleCenter != null) {
                    Card(
                        modifier = Modifier
                            .align(Alignment.TopCenter)
                            .padding(16.dp)
                    ) {
                        Text(
                            "관심 영역이 선택됨",
                            modifier = Modifier.padding(12.dp),
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
            
            // 하단 컨트롤
            Column(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // 설명 입력
                OutlinedTextField(
                    value = "",
                    onValueChange = {},
                    placeholder = { Text("증거에 대한 설명 입력...") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 16.dp),
                    singleLine = true
                )
                
                // 촬영 버튼
                Row(
                    horizontalArrangement = Arrangement.spacedBy(32.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // 갤러리 버튼
                    IconButton(
                        onClick = { /* 갤러리 */ },
                        modifier = Modifier.size(56.dp)
                    ) {
                        Icon(
                            Icons.Default.PhotoLibrary,
                            contentDescription = "갤러리",
                            modifier = Modifier.size(32.dp)
                        )
                    }
                    
                    // 촬영 버튼
                    FilledIconButton(
                        onClick = {
                            takePhoto(
                                imageCapture = imageCapture,
                                executor = executor,
                                context = context,
                                investigationId = investigationId,
                                focusArea = if (isCircleMode && circleCenter != null) {
                                    circleCenter?.let { center ->
                                        mapOf(
                                            "center_x" to center.x,
                                            "center_y" to center.y,
                                            "radius" to circleRadius
                                        )
                                    }
                                } else null,
                                onSuccess = { evidenceId ->
                                    onPhotoTaken(evidenceId)
                                }
                            )
                        },
                        modifier = Modifier.size(80.dp),
                        shape = CircleShape,
                        colors = IconButtonDefaults.filledIconButtonColors(
                            containerColor = FireRed
                        )
                    ) {
                        Icon(
                            Icons.Default.Camera,
                            contentDescription = "촬영",
                            modifier = Modifier.size(40.dp)
                        )
                    }
                    
                    // 음성 메모 버튼
                    IconButton(
                        onClick = { /* 음성 녹음 */ },
                        modifier = Modifier.size(56.dp)
                    ) {
                        Icon(
                            Icons.Default.Mic,
                            contentDescription = "음성 메모",
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun CameraPreview(
    context: Context,
    lifecycleOwner: androidx.lifecycle.LifecycleOwner,
    onImageCapture: (ImageCapture) -> Unit
) {
    val previewView = remember { PreviewView(context) }
    
    AndroidView(
        factory = { previewView },
        modifier = Modifier.fillMaxSize()
    ) { view ->
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()
            
            val preview = Preview.Builder()
                .build()
                .also { it.setSurfaceProvider(view.surfaceProvider) }
            
            val imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()
            
            onImageCapture(imageCapture)
            
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    preview,
                    imageCapture
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }, ContextCompat.getMainExecutor(context))
    }
}

@Composable
private fun CircleToSearchOverlay(
    circleCenter: Offset?,
    circleRadius: Float,
    onCircleChange: (Offset?, Float) -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.pointerInput(Unit) {
            detectDragGestures(
                onDragStart = { offset ->
                    onCircleChange(offset, circleRadius)
                },
                onDrag = { change, _ ->
                    change.consume()
                    onCircleChange(change.position, circleRadius)
                }
            )
        }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            circleCenter?.let { center ->
                // 원 그리기
                drawCircle(
                    color = FireRed,
                    radius = circleRadius,
                    center = center,
                    style = Stroke(width = 4f)
                )
                // 중심점
                drawCircle(
                    color = FireRed,
                    radius = 8f,
                    center = center
                )
            }
        }
    }
}

private fun takePhoto(
    imageCapture: ImageCapture?,
    executor: ExecutorService,
    context: Context,
    investigationId: Int,
    focusArea: Map<String, Float>?,
    onSuccess: (Int) -> Unit
) {
    val imageCapture = imageCapture ?: return
    
    val photoFile = File(
        context.cacheDir,
        SimpleDateFormat("yyyy-MM-dd-HH-mm-ss", Locale.KOREA)
            .format(System.currentTimeMillis()) + ".jpg"
    )
    
    val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()
    
    imageCapture.takePicture(
        outputOptions,
        executor,
        object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                // TODO: 서버에 업로드하고 evidenceId 받아오기
                // 지금은 더미 ID 반환
                onSuccess(1)
            }
            
            override fun onError(exception: ImageCaptureException) {
                exception.printStackTrace()
            }
        }
    )
}
