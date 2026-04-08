package com.fireinvestigation.data.model

import android.os.Parcelable
import kotlinx.parcelize.Parcelize
import java.util.Date

/**
 * API 모델 클래스들
 */

enum class InvestigationStatus {
    PENDING, IN_PROGRESS, ANALYZING, REVIEWING, COMPLETED, ARCHIVED
}

enum class FireCause {
    ELECTRICAL, GAS_LEAK, ARSON, ACCIDENTAL, MECHANICAL, CHEMICAL, UNKNOWN, OTHER
}

enum class UserRole {
    INVESTIGATOR, SUPERVISOR, ADMIN, FORENSIC_EXPERT
}

@Parcelize
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val fullName: String,
    val badgeNumber: String?,
    val department: String?,
    val role: UserRole,
    val isActive: Boolean,
    val createdAt: Date,
    val lastLogin: Date?
) : Parcelable

@Parcelize
data class Investigation(
    val id: Int,
    val caseNumber: String,
    val title: String,
    val description: String?,
    val address: String?,
    val latitude: Double?,
    val longitude: Double?,
    val incidentDateTime: Date?,
    val investigationDateTime: Date?,
    val status: InvestigationStatus,
    val predictedCause: FireCause?,
    val predictedCauseConfidence: Float?,
    val ignitionPoint: IgnitionPoint?,
    val analysisSummary: String?,
    val finalReport: String?,
    val isReportApproved: Boolean,
    val investigatorId: Int,
    val investigator: User?,
    val createdAt: Date,
    val updatedAt: Date?,
    val isSynced: Boolean
) : Parcelable

@Parcelize
data class IgnitionPoint(
    val x: Float,
    val y: Float,
    val confidence: Float,
    val description: String?,
    val method: String?
) : Parcelable

@Parcelize
data class Evidence(
    val id: Int,
    val investigationId: Int,
    val evidenceNumber: String,
    val fileName: String,
    val originalFileName: String,
    val filePath: String,
    val fileSize: Long,
    val fileType: String,
    val mimeType: String,
    val description: String?,
    val captureDateTime: Date?,
    val captureLocation: Location?,
    val hasBeenAnalyzed: Boolean,
    val isPiiBlurred: Boolean,
    val hashSha256: String?,
    val uploadedAt: Date,
    val isSynced: Boolean,
    val localPath: String? = null
) : Parcelable

@Parcelize
data class Location(
    val latitude: Double,
    val longitude: Double,
    val accuracy: Float? = null
) : Parcelable

@Parcelize
data class DetectedObject(
    val className: String,
    val confidence: Float,
    val bbox: BoundingBox
) : Parcelable

@Parcelize
data class BoundingBox(
    val x1: Float,
    val y1: Float,
    val x2: Float,
    val y2: Float,
    val centerX: Float,
    val centerY: Float
) : Parcelable

@Parcelize
data class FirePattern(
    val patternType: String,
    val description: String,
    val confidence: Float
) : Parcelable

@Parcelize
data class AnalysisResult(
    val id: Int,
    val investigationId: Int,
    val evidenceId: Int?,
    val analysisType: String,
    val detectedObjects: List<DetectedObject>,
    val firePatterns: List<FirePattern>?,
    val predictedCause: FireCause?,
    val causeConfidence: Float?,
    val ignitionPointEstimate: IgnitionPoint?,
    val processingTimeMs: Int,
    val modelVersion: String,
    val createdAt: Date
) : Parcelable

@Parcelize
data class SimilarCase(
    val id: Int,
    val externalCaseId: String,
    val title: String,
    val incidentDate: Date?,
    val location: String?,
    val fireCause: FireCause?,
    val damageSummary: String?,
    val lessonsLearned: String?,
    val similarityScore: Float
) : Parcelable

// 요청/응답 모델
data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val accessToken: String,
    val tokenType: String,
    val expiresIn: Int,
    val user: User
)

data class CreateInvestigationRequest(
    val title: String,
    val description: String?,
    val address: String?,
    val latitude: Double?,
    val longitude: Double?,
    val incidentDateTime: Date?
)

data class UpdateInvestigationRequest(
    val title: String?,
    val description: String?,
    val address: String?,
    val latitude: Double?,
    val longitude: Double?,
    val incidentDateTime: Date?,
    val status: InvestigationStatus?
)

data class AnalysisRequest(
    val evidenceId: Int,
    val analysisType: String = "full",
    val focusArea: FocusArea? = null
)

data class FocusArea(
    val centerX: Float,
    val centerY: Float,
    val radius: Float
)

data class ChatMessage(
    val role: String,
    val content: String
)

data class ChatRequest(
    val investigationId: Int,
    val message: String,
    val history: List<ChatMessage> = emptyList()
)

data class ChatResponse(
    val investigationId: Int,
    val response: String,
    val sources: List<Map<String, Any>>?,
    val confidence: Float?
)

data class PendingOperation(
    val id: String,
    val operation: String,
    val entityType: String,
    val entityId: String?,
    val payload: Map<String, Any>?,
    val fileAttachments: List<String>?,
    val createdAt: Date,
    val retryCount: Int = 0
)
