package com.pncp.monitor.domain.model;

import java.math.BigDecimal;

public record EditalLeve(
    String id,
    String objeto,
    String infoComplementar,
    String orgao,
    String uf,
    String municipio,
    String modalidade,
    BigDecimal valorEstimado,
    String dataAbertura,
    String dataSessao,
    String linkPncp
) {}
