package com.fireinvestigation.data.remote

import com.fireinvestigation.data.model.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

/**
 * REST API 인터페이스
 */
interface ApiService {

    // ========== 인증 ==========
    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("api/v1/auth/register")
    suspend fun register(@Body request: User): Response<User>

    @GET("api/v1/auth/me")
    suspend fun getCurrentUser(): Response<User>

    // ========== 화재 조사 ==========
    @GET("api/v1/investigations")
    suspend fun getInvestigations(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 20,
        @Query("status") status: InvestigationStatus? = null
    ): Response<InvestigationListResponse>

    @GET("api/v1/investigations/{id}")
    suspend fun getInvestigation(@Path("id") id: Int): Response<Investigation>

    @POST("api/v1/investigations")
    suspend fun createInvestigation(@Body request: CreateInvestigationRequest): Response<Investigation>

    @PUT("api/v1/investigations/{id}")
    suspend fun updateInvestigation(
        @Path("id") id: Int,
        @Body request: UpdateInvestigationRequest
    ): Response<Investigation>

    @DELETE("api/v1/investigations/{id}")
    suspend fun deleteInvestigation(@Path("id") id: Int): Response<Unit>

    // ========== 증거 자료 ==========
    @GET("api/v1/investigations/{id}/evidence")
    suspend fun getEvidenceList(@Path("id") investigationId: Int): Response<List<Evidence>>

    @Multipart
    @POST("api/v1/investigations/{id}/evidence")
    suspend fun uploadEvidence(
        @Path("id") investigationId: Int,
        @Part file: MultipartBody.Part,
        @Part("description") description: RequestBody?,
        @Part("capture_datetime") captureDateTime: RequestBody?,
        @Part("latitude") latitude: RequestBody?,
        @Part("longitude") longitude: RequestBody?
    ): Response<Evidence>

    // ========== AI 분석 ==========
    @POST("api/v1/investigations/{id}/analyze")
    suspend fun analyzeEvidence(
        @Path("id") investigationId: Int,
        @Body request: AnalysisRequest
    ): Response<AnalysisResponseWrapper>

    @POST("api/v1/investigations/{id}/report")
    suspend fun generateReport(
        @Path("id") investigationId: Int,
        @Body request: ReportGenerateRequest
    ): Response<ReportResponse>

    @POST("api/v1/investigations/{id}/chat")
    suspend fun chatWithAI(
        @Path("id") investigationId: Int,
        @Body request: ChatRequest
    ): Response<ChatResponse>

    // ========== 검색 ==========
    @POST("api/v1/search/circle-to-search")
    suspend fun circleToSearch(@Body request: CircleToSearchRequest): Response<CircleSearchResponse>

    @GET("api/v1/search/similar-cases/{investigationId}")
    suspend fun getSimilarCases(@Path("investigationId") investigationId: Int): Response<SimilarCasesResponse>

    @POST("api/v1/search/batch-analyze/{investigationId}")
    suspend fun batchAnalyze(@Path("investigationId") investigationId: Int): Response<BatchAnalysisResponse>

    // ========== 대시보드 ==========
    @GET("api/v1/dashboard/stats")
    suspend fun getDashboardStats(): Response<DashboardStats>

    @GET("api/v1/dashboard/recent-activity")
    suspend fun getRecentActivity(@Query("limit") limit: Int = 10): Response<List<ActivityItem>>

    // ========== 오프라인 동기화 ==========
    @POST("api/v1/sync")
    suspend fun syncPendingOperations(@Body request: SyncRequest): Response<SyncResponse>
}

// 응답 래퍼 클래스들
data class InvestigationListResponse(
    val total: Int,
    val items: List<Investigation>
)

data class AnalysisResponseWrapper(
    val analysisId: Int,
    val result: AnalysisResult,
    val message: String
)

data class ReportGenerateRequest(
    val includeAiAnalysis: Boolean = true,
    val includeEvidenceSummary: Boolean = true,
    val templateType: String = "standard"
)

data class ReportResponse(
    val investigationId: Int,
    val generatedReport: String,
    val generatedAt: String
)

data class CircleSearchResponse(
    val focusArea: FocusArea,
    val analysisResult: AnalysisResult,
    val similarCases: List<SimilarCase>
)

data class SimilarCasesResponse(
    val investigationId: Int,
    val similarCases: List<SimilarCase>,
    val totalFound: Int
)

data class BatchAnalysisResponse(
    val investigationId: Int,
    val total: Int,
    val processed: Int,
    val failed: Int,
    val results: List<BatchResultItem>
)

data class BatchResultItem(
    val evidenceId: Int,
    val status: String,
    val predictedCause: FireCause?,
    val error: String?
)

data class DashboardStats(
    val totalInvestigations: Int,
    val investigationsThisMonth: Int,
    val pendingAnalysis: Int,
    val completedReports: Int,
    val recentCases: List<Investigation>,
    val causeDistribution: Map<String, Int>,
    val averageProcessingTime: Float?
)

data class ActivityItem(
    val id: Int,
    val timestamp: String,
    val username: String,
    val action: String,
    val resourceType: String,
    val resourceId: String,
    val investigationId: Int?,
    val success: Boolean
)

data class SyncRequest(
    val deviceId: String,
    val pendingOperations: List<PendingOperation>
)

data class SyncResponse(
    val syncedCount: Int,
    val failedCount: Int,
    val conflicts: List<Map<String, Any>>?
)
