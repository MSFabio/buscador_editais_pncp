package com.pncp.monitor.domain.model;

public record PalavraChave(
    String id,
    String termo,
    String contexto,
    boolean ativa
) {}
