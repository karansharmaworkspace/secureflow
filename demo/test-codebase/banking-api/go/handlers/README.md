# Go Handlers

All Go banking API handlers are defined inline in `main.go` (60 lines). This directory is intentionally empty — it exists as a placeholder for potential handler extraction.

The handlers use Gin framework's `gin.H` for JSON responses and follow the pattern:
```go
func handlerName(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{...})
}
```

No handler files have been extracted to this directory yet. All 6 Forex API routes remain in `main.go` as inline anonymous-style handlers registered in the `main()` function.
