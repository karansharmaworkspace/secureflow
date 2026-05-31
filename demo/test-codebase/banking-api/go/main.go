package main

import (
	"net/http"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.GET("/api/v3/forex/rates", getForexRates)
	r.POST("/api/v3/forex/convert", convertCurrency)
	r.GET("/api/v3/forex/history", getForexHistory)
	r.POST("/api/v3/forex/remittance", initiateRemittance)
	r.GET("/api/v3/forex/travel-card/load", loadTravelCard)
	r.GET("/api/v3/forex/alerts", getRateAlerts)

	r.Run(":8080")
}

func getForexRates(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"USD": 83.25,
		"EUR": 90.10,
		"GBP": 105.50,
		"JPY": 0.55,
	})
}

func convertCurrency(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"converted": true,
		"rate": 83.25,
	})
}

func getForexHistory(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"history": []string{},
	})
}

func initiateRemittance(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"remittance_id": "REM123456",
		"status": "initiated",
	})
}

func loadTravelCard(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"loaded": true,
	})
}

func getRateAlerts(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"alerts": []string{},
	})
}
