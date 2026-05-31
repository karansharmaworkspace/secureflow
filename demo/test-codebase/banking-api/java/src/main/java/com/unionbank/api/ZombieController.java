package com.unionbank.api;

/**
 * DEPRECATED - Legacy service endpoint.
 * This controller is deprecated since v2 migration.
 * TODO: remove this entire class
 */
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/v1/admin")
public class ZombieController {

    @GetMapping("/users")
    public Map<String, Object> listUsers() {
        return Map.of("users", List.of(), "deprecated", true);
    }

    @PostMapping("/users/create")
    public Map<String, Object> createUser() {
        return Map.of("created", true, "legacy", true);
    }

    @GetMapping("/config")
    public Map<String, Object> getConfig() {
        return Map.of("debug", true, "version", "1.0.0");
    }

    @GetMapping("/temp/health")
    public Map<String, Object> tempHealth() {
        return Map.of("ok", true, "temporary", true);
    }

    @PostMapping("/mock/deploy")
    public Map<String, Object> mockDeploy() {
        return Map.of("mock", true);
    }
}
