package com.demo.aicontext.controller;

// ErrorController.java
import org.springframework.boot.web.error.ErrorAttributeOptions;
import org.springframework.boot.web.servlet.error.ErrorAttributes;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.context.request.WebRequest;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Map;

@Controller
public class CustomErrorController implements org.springframework.boot.web.servlet.error.ErrorController {

    private final ErrorAttributes errorAttributes;

    public CustomErrorController(ErrorAttributes errorAttributes) {
        this.errorAttributes = errorAttributes;
    }

    @RequestMapping("/error")
    public String handleError(HttpServletRequest request, WebRequest webRequest, Model model) {
        Map<String, Object> errors = errorAttributes.getErrorAttributes(
            webRequest,
            ErrorAttributeOptions.of(
                ErrorAttributeOptions.Include.MESSAGE,
                ErrorAttributeOptions.Include.BINDING_ERRORS,
                ErrorAttributeOptions.Include.EXCEPTION
            )
        );

        Integer statusCode = (Integer) errors.get("status");
        String message = (String) errors.get("message");
        String path = (String) errors.get("path");
        String error = (String) errors.get("error");

        model.addAttribute("statusCode", statusCode != null ? statusCode : 500);
        model.addAttribute("error", error != null ? error : "Unknown Error");
        model.addAttribute("message", message != null ? message : "An unexpected error occurred");
        model.addAttribute("path", path != null ? path : "");

        return "error";
    }
}
