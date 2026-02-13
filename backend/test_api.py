"""Tests for the satellite image geolocation prediction API."""

import io
import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport

from main import app, lifespan
from predict import Predictor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_image_bytes(
    size: tuple[int, int] = (256, 256),
    color: str | tuple = "blue",
    fmt: str = "PNG",
) -> bytes:
    """Create an in-memory image and return its bytes."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


def make_grayscale_image_bytes(
    size: tuple[int, int] = (256, 256),
    value: int = 128,
) -> bytes:
    """Create a grayscale image and return PNG bytes."""
    img = Image.new("L", size, value)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def make_rgba_image_bytes(
    size: tuple[int, int] = (256, 256),
    color: tuple = (0, 100, 200, 128),
) -> bytes:
    """Create an RGBA image with transparency and return PNG bytes."""
    img = Image.new("RGBA", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def predictor():
    return Predictor()


@pytest.fixture()
async def client():
    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


# ---------------------------------------------------------------------------
# Unit tests – Predictor class
# ---------------------------------------------------------------------------

class TestPredictor:
    """Test the Predictor class directly with various image types."""

    def test_predict_rgb_image(self, predictor: Predictor):
        img = Image.new("RGB", (256, 256), color="blue")
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result
        assert isinstance(result["longitude"], float)
        assert isinstance(result["latitude"], float)

    def test_predict_grayscale_image(self, predictor: Predictor):
        img = Image.new("L", (128, 128), 200)
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result

    def test_predict_rgba_image(self, predictor: Predictor):
        img = Image.new("RGBA", (512, 512), (255, 0, 0, 128))
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result

    def test_predict_small_image(self, predictor: Predictor):
        img = Image.new("RGB", (16, 16), "green")
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result

    def test_predict_large_image(self, predictor: Predictor):
        img = Image.new("RGB", (2048, 2048), "red")
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result

    def test_predict_non_square_image(self, predictor: Predictor):
        img = Image.new("RGB", (640, 480), "yellow")
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result

    def test_predict_1x1_image(self, predictor: Predictor):
        img = Image.new("RGB", (1, 1), "white")
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result

    def test_different_colors_give_different_predictions(self, predictor: Predictor):
        """Different images should generally produce different predictions."""
        white = predictor.predict(Image.new("RGB", (256, 256), "white"))
        black = predictor.predict(Image.new("RGB", (256, 256), "black"))
        # At least one coordinate should differ
        assert (
            white["longitude"] != black["longitude"]
            or white["latitude"] != black["latitude"]
        )

    def test_same_image_gives_consistent_predictions(self, predictor: Predictor):
        """The same image should always produce the same prediction."""
        img = Image.new("RGB", (256, 256), (42, 128, 200))
        r1 = predictor.predict(img)
        r2 = predictor.predict(img)
        assert r1["longitude"] == pytest.approx(r2["longitude"])
        assert r1["latitude"] == pytest.approx(r2["latitude"])

    def test_predict_palette_mode_image(self, predictor: Predictor):
        """Palette (P) mode images should be handled via RGB conversion."""
        img = Image.new("P", (128, 128))
        result = predictor.predict(img)
        assert "longitude" in result
        assert "latitude" in result

    def test_predict_jpeg_saved_image(self, predictor: Predictor):
        """Round-trip through JPEG encoding should still work."""
        img = Image.new("RGB", (256, 256), (100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        reloaded = Image.open(buf)
        result = predictor.predict(reloaded)
        assert "longitude" in result
        assert "latitude" in result


# ---------------------------------------------------------------------------
# Integration tests – FastAPI endpoint
# ---------------------------------------------------------------------------

class TestPredictEndpoint:
    """Test the POST /predict endpoint."""

    @pytest.mark.anyio
    async def test_predict_png(self, client: AsyncClient):
        data = make_image_bytes(color="blue", fmt="PNG")
        response = await client.post(
            "/predict",
            files={"file": ("test.png", data, "image/png")},
        )
        assert response.status_code == 200
        body = response.json()
        assert "longitude" in body
        assert "latitude" in body

    @pytest.mark.anyio
    async def test_predict_jpeg(self, client: AsyncClient):
        data = make_image_bytes(color="red", fmt="JPEG")
        response = await client.post(
            "/predict",
            files={"file": ("test.jpg", data, "image/jpeg")},
        )
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body["longitude"], float)
        assert isinstance(body["latitude"], float)

    @pytest.mark.anyio
    async def test_predict_grayscale_upload(self, client: AsyncClient):
        data = make_grayscale_image_bytes()
        response = await client.post(
            "/predict",
            files={"file": ("gray.png", data, "image/png")},
        )
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_predict_rgba_upload(self, client: AsyncClient):
        data = make_rgba_image_bytes()
        response = await client.post(
            "/predict",
            files={"file": ("rgba.png", data, "image/png")},
        )
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_reject_non_image_content_type(self, client: AsyncClient):
        response = await client.post(
            "/predict",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_reject_corrupt_image(self, client: AsyncClient):
        response = await client.post(
            "/predict",
            files={"file": ("bad.png", b"not valid png data", "image/png")},
        )
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_no_file_returns_422(self, client: AsyncClient):
        response = await client.post("/predict")
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_multiple_sizes(self, client: AsyncClient):
        """Multiple image sizes should all succeed."""
        for size in [(64, 64), (128, 128), (512, 512)]:
            data = make_image_bytes(size=size, color="green")
            response = await client.post(
                "/predict",
                files={"file": (f"test_{size[0]}.png", data, "image/png")},
            )
            assert response.status_code == 200, f"Failed for size {size}"
