package com.unionbank.api;

import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/v3/loans")
public class LoanController {

    @GetMapping("/{loanId}/status")
    public Map<String, Object> getLoanStatus(@PathVariable String loanId) {
        Map<String, Object> result = new HashMap<>();
        result.put("loan_id", loanId);
        result.put("status", "active");
        result.put("emi_remaining", 48);
        return result;
    }

    @GetMapping("/{loanId}/schedule")
    public Map<String, Object> getEmiSchedule(@PathVariable String loanId) {
        Map<String, Object> result = new HashMap<>();
        result.put("loan_id", loanId);
        result.put("schedule", List.of());
        return result;
    }

    @PostMapping("/{loanId}/prepayment")
    public Map<String, Object> prepayment(@PathVariable String loanId, @RequestParam double amount) {
        Map<String, Object> result = new HashMap<>();
        result.put("accepted", true);
        result.put("amount", amount);
        return result;
    }

    @GetMapping("/{loanId}/documents")
    public Map<String, Object> getLoanDocuments(@PathVariable String loanId) {
        Map<String, Object> result = new HashMap<>();
        result.put("loan_id", loanId);
        result.put("documents", List.of());
        return result;
    }
}
