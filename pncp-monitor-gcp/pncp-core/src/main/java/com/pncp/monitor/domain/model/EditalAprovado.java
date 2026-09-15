package com.pncp.monitor.domain.model;

import java.math.BigDecimal;
import java.time.Instant;

public record EditalAprovado(
    String id,
    String objeto,
    String orgao,
    String uf,
    String municipio,
    String modalidade,
    BigDecimal valorEstimado,
    String dataAbertura,
    String dataSessao,
    String linkPncp,
    String justificativaGemini,
    double confiancaGemini,
    String keywordOrigem,
    Instant processadoEm
) {
    public static EditalAprovado fromEditalLeve(
        EditalLeve edital, VeredictoGemini veredicto, String keyword, Instant processadoEm
    ) {
        return new EditalAprovado(
            edital.id(), edital.objeto(), edital.orgao(), edital.uf(),
            edital.municipio(), edital.modalidade(), edital.valorEstimado(),
            edital.dataAbertura(), edital.dataSessao(), edital.linkPncp(),
            veredicto.justificativa(), veredicto.confianca(), keyword, processadoEm
        );
    }
}
