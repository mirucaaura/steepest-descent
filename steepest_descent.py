import numpy as np
from scipy.optimize import fmin
from nptyping import NDArray
from typing import Any, Callable
from dataclasses import dataclass

@dataclass
class SteepestDescent:
    ndim: int
    nu: float
    sigma: float
    eps: float
    
    def f1(self, x: NDArray[(1, ...), np.float64]) -> Any:
        return x[0]**2 + 3 * (x[1] - 1)**2

    def f2(self, x: NDArray[(1, ...), np.float64]) -> Any:
        return 2 * (x[0] - 1)**2 + x[1]**2

    def F(self, x: NDArray[(1, ...), np.float64]) -> NDArray[(1, ...), np.float64]:
        return np.array([self.f1(x), self.f2(x)])

    def grad(self, f: Callable[[NDArray[(1, ...), np.float64]], float], x: NDArray[(1, ...), np.float64], h=1e-4) -> NDArray[(1, ...), np.float64]:
        g = np.zeros_like(x)
        for i in range(self.ndim):
            tmp = x[i]
            x[i] = tmp + h
            yr = f(x)
            x[i] = tmp - h
            yl = f(x)
            g[i] = (yr - yl) / (2 * h)
            x[i] = tmp
        return g

    def nabla_F(self, x: NDArray[(1, ...), np.float64]) -> NDArray[(Any, ...), np.float64]:
        return np.array([self.grad(self.f1, x), self.grad(self.f2, x)])

    def phi(self, d: NDArray[(1, ...), np.float64], x: NDArray[(1, ...), np.float64]) -> Any:
        nabla_F = self.nabla_F(x)
        return max(np.dot(nabla_F, d)) + 0.5 * np.linalg.norm(d) ** 2

    def theta(self, d: NDArray[(1, ...), np.float64], x: NDArray[(1, ...), np.float64]) -> Any:
        return self.phi(d, x) + 0.5 * np.linalg.norm(d) ** 2

    def armijo(self, d: NDArray[(1, ...), np.float64], x: NDArray[(1, ...), np.float64]) -> float:
        power = 0
        t = pow(self.nu, power)
        Fl = np.array(self.F(x + t * d))
        Fr = np.array(self.F(x))
        Re = self.sigma * t * np.dot(self.nabla_F(x), d)
        while np.all(Fl > Fr + Re):
            t *= self.nu
            Fl = np.array(self.F(x + t * d))
            Fr = np.array(self.F(x))
            Re = self.sigma * t * np.dot(self.nabla_F(x), d)
        return t
    
    def steepest(self, x: NDArray[(1, ...), np.float64]) -> NDArray[(1, ...), np.float64]:
        d = np.array(fmin(self.phi, x, args=(x, )))
        th = self.theta(d, x)
        while abs(th) > self.eps:
            t = self.armijo(d, x)
            x = x + t * d
            d = np.array(fmin(self.phi, x, args=(x, )))
            th = self.theta(d, x)
        return x