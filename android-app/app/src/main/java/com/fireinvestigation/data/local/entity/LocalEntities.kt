package com.fireinvestigation.data.local.entity

import androidx.room.*
import com.fireinvestigation.data.model.FireCause
import com.fireinvestigation.data.model.InvestigationStatus
import java.util.Date

@Entity(tableName = "investigations")
data class LocalInvestigation(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    
    @ColumnInfo(name = "server_id")
    val serverId: Int? = null,
    
    val caseNumber: String? = null,
    val title: String,
    val description: String?,
    val address: String?,
    val latitude: Double?,
    val longitude: Double?,
    val incidentDateTime: Date?,
    val investigationDateTime: Date?,
    
    @ColumnInfo(name = "status")
    val status: InvestigationStatus = InvestigationStatus.PENDING,
    
    @ColumnInfo(name = "predicted_cause")
    val predictedCause: FireCause? = null,
    
    @ColumnInfo(name = "predicted_cause_confidence")
    val predictedCauseConfidence: Float? = null,
    
    @ColumnInfo(name = "analysis_summary")
    val analysisSummary: String? = null,
    
    @ColumnInfo(name = "final_report")
    val finalReport: String? = null,
    
    @ColumnInfo(name = "investigator_id")
    val investigatorId: Int,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Date = Date(),
    
    @ColumnInfo(name = "updated_at")
    val updatedAt: Date = Date(),
    
    @ColumnInfo(name = "is_synced")
    val isSynced: Boolean = false,
    
    @ColumnInfo(name = "pending_operation")
    val pendingOperation: String? = null
)

@Entity(
    tableName = "evidence",
    foreignKeys = [
        ForeignKey(
            entity = LocalInvestigation::class,
            parentColumns = ["id"],
            childColumns = ["local_investigation_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("local_investigation_id")]
)
data class LocalEvidence(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    
    @ColumnInfo(name = "server_id")
    val serverId: Int? = null,
    
    @ColumnInfo(name = "local_investigation_id")
    val localInvestigationId: Int,
    
    @ColumnInfo(name = "investigation_id")
    val investigationId: Int? = null,
    
    val evidenceNumber: String? = null,
    val fileName: String,
    val originalFileName: String,
    
    @ColumnInfo(name = "local_path")
    val localPath: String,
    
    @ColumnInfo(name = "server_path")
    val serverPath: String? = null,
    
    @ColumnInfo(name = "file_size")
    val fileSize: Long,
    
    @ColumnInfo(name = "file_type")
    val fileType: String,
    
    @ColumnInfo(name = "mime_type")
    val mimeType: String,
    
    val description: String?,
    
    @ColumnInfo(name = "capture_date_time")
    val captureDateTime: Date?,
    
    @ColumnInfo(name = "capture_latitude")
    val captureLatitude: Double?,
    
    @ColumnInfo(name = "capture_longitude")
    val captureLongitude: Double?,
    
    @ColumnInfo(name = "has_been_analyzed")
    val hasBeenAnalyzed: Boolean = false,
    
    @ColumnInfo(name = "is_pii_blurred")
    val isPiiBlurred: Boolean = false,
    
    @ColumnInfo(name = "hash_sha256")
    val hashSha256: String? = null,
    
    @ColumnInfo(name = "uploaded_at")
    val uploadedAt: Date = Date(),
    
    @ColumnInfo(name = "is_synced")
    val isSynced: Boolean = false,
    
    @ColumnInfo(name = "pending_operation")
    val pendingOperation: String? = null
)

@Entity(tableName = "pending_operations")
data class PendingOperationEntity(
    @PrimaryKey
    val id: String,
    
    @ColumnInfo(name = "operation")
    val operation: String,
    
    @ColumnInfo(name = "entity_type")
    val entityType: String,
    
    @ColumnInfo(name = "local_id")
    val localId: Int?,
    
    @ColumnInfo(name = "server_id")
    val serverId: Int?,
    
    @ColumnInfo(name = "payload_json")
    val payloadJson: String?,
    
    @ColumnInfo(name = "file_attachments")
    val fileAttachments: String?,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Date = Date(),
    
    @ColumnInfo(name = "retry_count")
    val retryCount: Int = 0,
    
    @ColumnInfo(name = "error_message")
    val errorMessage: String? = null,
    
    @ColumnInfo(name = "status")
    val status: String = "pending"
)

@Entity(tableName = "user_profile")
data class UserProfile(
    @PrimaryKey
    val id: Int,
    val username: String,
    val email: String,
    val fullName: String,
    val badgeNumber: String?,
    val department: String?,
    val role: String,
    val token: String?,
    val tokenExpiry: Date?,
    val lastSync: Date?
)

@Entity(tableName = "analysis_cache")
data class AnalysisCache(
    @PrimaryKey
    val evidenceId: Int,
    
    @ColumnInfo(name = "result_json")
    val resultJson: String,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Date = Date(),
    
    @ColumnInfo(name = "expires_at")
    val expiresAt: Date?
)
