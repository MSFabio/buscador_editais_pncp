package com.pncp.monitor.domain.model;

public record VeredictoGemini(
    String editalId,
    boolean aderente,
    String justificativa,
    double confianca
) {}
