package com.pncp.monitor.domain.model;

import java.util.List;

public record ConfiguracaoNotificacao(
    String id,
    List<String> emails
) {}
