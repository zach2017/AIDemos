package com.demo.aicontext;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@EnableAsync
@SpringBootApplication
public class AicontextApplication {

	public static void main(String[] args) {
		SpringApplication.run(AicontextApplication.class, args);
	}

}
