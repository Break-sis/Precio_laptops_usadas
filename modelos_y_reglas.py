"""Módulo de modelos de datos (SQLModel) y reglas de negocio para UAT."""

from sqlmodel import Field, Session, SQLModel, create_engine, select


class Pedido(SQLModel, table=True):
    """Representa un pedido registrado en el sistema."""

    id: int | None = Field(default=None, primary_key=True)
    cliente: str
    cantidad: int
    precio_unitario: float
    descuento_aplicado: float = 0.0
    envio: float = 0.0
    total: float


def crear_engine_sqlite(url: str = "sqlite:///pedidos_clase.db"):
    """Crea el motor SQLite y garantiza que las tablas existan."""
    engine = create_engine(url, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def registrar_pedido(
    session: Session,
    cliente: str,
    cantidad: int,
    precio_unitario: float,
) -> tuple[bool, str, Pedido | None]:
    """Evalúa las reglas de aceptación de negocio y persiste el pedido si es válido.

    Reglas de negocio:
    1. El nombre del cliente no puede estar vacío.
    2. La cantidad debe ser un entero mayor a 0.
    3. El precio unitario debe ser mayor a 0.
    4. Si la cantidad es >= 10 unidades, se aplica 15% de descuento. Si es >= 5, 10%.
    5. El costo de envío estándar es $5.00, pero es GRATIS ($0.00) si el subtotal
       con descuento supera o iguala $50.00.
    """
    nombre_limpio = cliente.strip()
    if not nombre_limpio:
        return False, "El nombre del cliente es obligatorio.", None

    if cantidad <= 0:
        return False, "La cantidad debe ser mayor a cero.", None

    if precio_unitario <= 0:
        return False, "El precio unitario debe ser mayor a cero.", None

    subtotal = cantidad * precio_unitario
    
    # NUEVA REGLA DE NEGOCIO (Evolución RN-03)
    if cantidad >= 10:
        tasa_descuento = 0.15
    elif cantidad >= 5:
        tasa_descuento = 0.10
    else:
        tasa_descuento = 0.0
        
    descuento = round(subtotal * tasa_descuento, 2)
    subtotal_con_descuento = round(subtotal - descuento, 2)

    envio = 0.0 if subtotal_con_descuento >= 50.0 else 5.0
    total_final = round(subtotal_con_descuento + envio, 2)

    pedido = Pedido(
        cliente=nombre_limpio,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
        descuento_aplicado=descuento,
        envio=envio,
        total=total_final,
    )
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return True, "Pedido registrado correctamente.", pedido


def listar_pedidos(session: Session) -> list[Pedido]:
    """Devuelve todos los pedidos almacenados ordenados por ID."""
    statement = select(Pedido).order_by(Pedido.id)
    return list(session.exec(statement).all())