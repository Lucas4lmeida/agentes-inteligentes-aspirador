import contextlib
import io
import unittest
from unittest.mock import patch

import agentes


class ConfiguracoesTest(unittest.TestCase):
    def test_grade_1x1_sempre_tem_inicio_livre(self):
        for semente in range(10):
            for sujeira, obstaculos, inicio in agentes.gerar_cenarios(30, semente, tamanho=1):
                self.assertEqual(inicio, (0, 0))
                self.assertEqual(obstaculos, set())
                self.assertEqual(sujeira, {(0, 0)})

    def test_obstaculos_nao_ocupam_toda_a_grade(self):
        for sujeira, obstaculos, inicio in agentes.gerar_cenarios(100, 42, tamanho=2, max_obstaculos=20):
            self.assertLessEqual(len(obstaculos), 3)
            self.assertNotIn(inicio, obstaculos)
            self.assertFalse(sujeira & obstaculos)

    def test_gerador_rejeita_configuracoes_invalidas(self):
        for kwargs in ({'tamanho': 0}, {'max_obstaculos': -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                agentes.gerar_cenarios(1, 42, **kwargs)

    def test_replay_com_um_cenario(self):
        with patch.object(agentes, 'CENARIOS', agentes.CENARIOS[:1]), patch.object(agentes, 'reproduzir') as replay:
            agentes.main(['--replay', '--atraso', '0'])
            self.assertTrue(replay.call_args.args[0]['titulo'].startswith('Cenario 1:'))

    def test_replay_aceita_quarto_cenario(self):
        cenarios = agentes.CENARIOS + [agentes.CENARIOS[0]]
        with patch.object(agentes, 'CENARIOS', cenarios), patch.object(agentes, 'reproduzir') as replay:
            agentes.main(['--replay', '--cenario', '4', '--atraso', '0'])
            self.assertTrue(replay.call_args.args[0]['titulo'].startswith('Cenario 4:'))

    def test_replay_rejeita_cenario_inexistente(self):
        with patch.object(agentes, 'CENARIOS', agentes.CENARIOS[:1]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as erro:
                agentes.main(['--replay', '--cenario', '2'])
            self.assertEqual(erro.exception.code, 2)

    def test_lista_vazia_tem_mensagem_clara(self):
        with patch.object(agentes, 'CENARIOS', []), contextlib.redirect_stderr(io.StringIO()) as saida:
            with self.assertRaises(SystemExit) as erro:
                agentes.main([])
            self.assertEqual(erro.exception.code, 2)
            self.assertIn('Adicione pelo menos um cenario', saida.getvalue())

    def test_resultados_fixos_preservados(self):
        esperados = [
            [(1174, 1098, 76, None), (1256, 1241, 15, 20)],
            [(1009, 932, 77, None), (1083, 1070, 13, 18)],
            [(1009, 933, 76, None), (1071, 1052, 19, 24)],
        ]
        for cenario, pares in zip(agentes.CENARIOS, esperados):
            for classe, esperado in zip((agentes.ReativoSimples, agentes.ReativoComMemoria), pares):
                resultado = agentes.simular(classe(), *cenario)
                self.assertEqual(tuple(resultado[k] for k in ('p1', 'p2', 'movimentos', 'parou')), esperado)


if __name__ == '__main__':
    unittest.main()
