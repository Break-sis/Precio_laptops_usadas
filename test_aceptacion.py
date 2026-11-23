"""Suite de Pruebas de Aceptación de Usuario (UAT) automatizadas con pytest."""

import pytest
from sqlmodel import Session

from modelos_y_reglas import crear_engine_sqlite, listar_pedidos, registrar_pedido


@pytest.fixture
def sesion_uat():
    """Provee una base de datos SQLite en memoria limpia por cada escenario UAT."""
    engine = crear_engine_sqlite("sqlite:///:memory:")
    with Session(engine) as session:
        yield session


def test_uat_01_pedido_estandar_sin_descuento_con_costo_envio(sesion_uat):
    """Escenario UAT-01: Compra menor a 5 unidades y menor a $50 cobra envío estándar."""
    ok, mensaje, pedido = registrar_pedido(sesion_uat, "Luis Pérez", 2, 15.0)

    assert ok is True
    assert pedido is not None
    assert pedido.descuento_aplicado == 0.0
    assert pedido.envio == 5.0
    assert pedido.total == 35.0
    assert len(listar_pedidos(sesion_uat)) == 1


def test_uat_02_pedido_por_volumen_aplica_descuento_y_envio_gratis(sesion_uat):
    """Escenario UAT-02: Compra de 5 o más unidades con subtotal >= $50 obtiene 10% desc. y envío gratis."""
    ok, mensaje, pedido = registrar_pedido(sesion_uat, "Ana López", 5, 20.0)

    assert ok is True
    assert pedido is not None
    assert pedido.descuento_aplicado == 10.0
    assert pedido.envio == 0.0
    assert pedido.total == 90.0


def test_uat_03_rechazo_cantidad_invalida_no_persiste_en_bd(sesion_uat):
    """Escenario UAT-03: Cantidad cero o negativa es rechazada con mensaje claro sin guardar."""
    ok, mensaje, pedido = registrar_pedido(sesion_uat, "Carlos Ruiz", 0, 25.0)

    assert ok is False
    assert pedido is None
    assert "mayor a cero" in mensaje.lower()
    assert len(listar_pedidos(sesion_uat)) == 0


# ---------------------------------------------------------------------------
# ESCENARIOS UAT-04 y UAT-05 (PARTE B)
# ---------------------------------------------------------------------------

def test_uat_04_descuento_por_volumen_pero_sin_envio_gratis(sesion_uat):
    """Escenario UAT-04: Descuento aplicado pero subtotal final < $50, por lo que cobra envío."""
    ok, mensaje, pedido = registrar_pedido(sesion_uat, "María Gomez", 5, 10.0)

    assert ok is True
    assert pedido is not None
    assert pedido.descuento_aplicado == 5.0
    assert pedido.envio == 5.0
    assert pedido.total == 50.0
    assert len(listar_pedidos(sesion_uat)) == 1


def test_uat_05_rechazo_cliente_vacio_o_con_espacios(sesion_uat):
    """Escenario UAT-05: El sistema rechaza pedidos donde el cliente está vacío o son espacios."""
    ok, mensaje, pedido = registrar_pedido(sesion_uat, "   ", 3, 12.0)

    assert ok is False
    assert pedido is None
    assert len(listar_pedidos(sesion_uat)) == 0


# ---------------------------------------------------------------------------
# ESCENARIO UAT-06 (PARTE C)
# ---------------------------------------------------------------------------

def test_uat_06_evolucion_descuento_15_por_ciento(sesion_uat):
    """Escenario UAT-06: Para pedidos de 10 o más unidades, el descuento sube al 15%."""
    # Dado que un cliente registra 10 unidades a $20.00 (subtotal inicial = $200.00)
    ok, mensaje, pedido = registrar_pedido(sesion_uat, "Roberto", 10, 20.0)

    # Entonces aplica 15% de descuento ($30.0), envío $0.0 y total $170.0
    assert ok is True
    assert pedido is not None
    assert pedido.descuento_aplicado == 30.0
    assert pedido.envio == 0.0
    assert pedido.total == 170.0
    assert len(listar_pedidos(sesion_uat)) == 1