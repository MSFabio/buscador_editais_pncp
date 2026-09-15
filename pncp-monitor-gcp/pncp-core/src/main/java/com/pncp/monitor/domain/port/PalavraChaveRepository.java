package com.pncp.monitor.domain.port;

import com.pncp.monitor.domain.model.PalavraChave;
import java.util.List;

public interface PalavraChaveRepository {
    List<PalavraChave> listarTodas();
    List<PalavraChave> listarAtivas();
    PalavraChave salvar(PalavraChave keyword);
    void remover(String id);
}
