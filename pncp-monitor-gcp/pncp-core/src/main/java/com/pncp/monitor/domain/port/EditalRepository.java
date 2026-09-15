package com.pncp.monitor.domain.port;

import com.pncp.monitor.domain.model.EditalAprovado;
import java.time.Instant;
import java.util.List;

public interface EditalRepository {
    void salvar(EditalAprovado edital);
    boolean existeById(String id);
    List<EditalAprovado> buscarPorPeriodo(Instant inicio, Instant fim);
}
