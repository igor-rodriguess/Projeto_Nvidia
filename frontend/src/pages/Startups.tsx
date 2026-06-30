import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, LayoutGrid, List, Filter } from 'lucide-react'
import { StartupCard } from '@/components/startup/StartupCard'
import { StartupTable } from '@/components/startup/StartupTable'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { useStartups } from '@/hooks/useStartups'
import type { MaturityClass } from '@/types/api'

const MATURITY_OPTIONS: MaturityClass[] = ['AI-native', 'AI-enabled', 'API-consumer', 'Non-AI']

export default function Startups() {
  const [searchParams] = useSearchParams()
  const { startups, loading, error, refetch } = useStartups(100)
  const [search, setSearch] = useState(searchParams.get('q') ?? '')
  const [classificationFilter, setClassificationFilter] = useState<MaturityClass | ''>('')
  const [levelFilter, setLevelFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [cityFilter, setCityFilter] = useState('')
  const [view, setView] = useState<'grid' | 'list'>('list')

  useEffect(() => {
    setSearch(searchParams.get('q') ?? '')
  }, [searchParams])

  const cities = [...new Set(startups.map((s) => s.cidade).filter(Boolean))] as string[]

  const filtered = startups.filter((s) => {
    const matchSearch =
      !search ||
      s.nome.toLowerCase().includes(search.toLowerCase()) ||
      s.categoria?.toLowerCase().includes(search.toLowerCase())
    const matchCity = !cityFilter || s.cidade === cityFilter
    const matchClassification = !classificationFilter || s.maturity_class === classificationFilter
    const matchLevel = !levelFilter || String(s.maturity_level) === levelFilter
    const matchStatus = !statusFilter || s.pipeline_runs?.[0]?.status === statusFilter
    return matchSearch && matchCity && matchClassification && matchLevel && matchStatus
  })

  const maturityMap = Object.fromEntries(
    startups
      .filter((startup) => startup.maturity_class && startup.maturity_class !== 'unknown')
      .map((startup) => [startup.id, startup.maturity_class as MaturityClass])
  )

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      {/* Filters bar */}
      <div
        style={{
          display: 'flex',
          gap: '0.75rem',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        {/* Search */}
        <div style={{ position: 'relative', flex: 1, minWidth: 220 }}>
          <Search
            size={14}
            style={{
              position: 'absolute', left: '0.75rem', top: '50%',
              transform: 'translateY(-50%)', color: 'var(--text-muted)',
              pointerEvents: 'none',
            }}
          />
          <input
            className="input"
            placeholder="Buscar por nome ou categoria…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ paddingLeft: '2.25rem' }}
            aria-label="Buscar startups"
          />
        </div>

        {/* Maturity filter */}
        <div style={{ position: 'relative' }}>
          <Filter
            size={13}
            style={{
              position: 'absolute', left: '0.75rem', top: '50%',
              transform: 'translateY(-50%)', color: 'var(--text-muted)',
              pointerEvents: 'none',
            }}
          />
          <select
            className="input"
            value={classificationFilter}
            onChange={(e) => setClassificationFilter(e.target.value as MaturityClass | '')}
            style={{ paddingLeft: '2.25rem', width: 170 }}
            aria-label="Filtrar por classificacao de IA"
          >
            <option value="">Classificacao</option>
            {MATURITY_OPTIONS.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <select className="input" value={levelFilter} onChange={(event) => setLevelFilter(event.target.value)} style={{ width: 150 }} aria-label="Filtrar por nivel de maturidade">
          <option value="">Nivel 0-5</option>
          {[0, 1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>Nivel {level}</option>)}
        </select>

        <select className="input" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} style={{ width: 150 }} aria-label="Filtrar por status da execucao">
          <option value="">Status</option>
          <option value="completed">Concluida</option><option value="partial">Parcial</option><option value="failed">Falha</option><option value="running">Executando</option><option value="pending">Pendente</option>
        </select>

        {/* City filter */}
        <select
          className="input"
          value={cityFilter}
          onChange={(e) => setCityFilter(e.target.value)}
          style={{ width: 160 }}
          aria-label="Filtrar por cidade"
        >
          <option value="">Cidade</option>
          {cities.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        {/* View toggle */}
        <div className="flex" style={{ border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <button
            className={`btn ${view === 'grid' ? 'btn-primary' : 'btn-ghost'}`}
            style={{ borderRadius: 0 }}
            onClick={() => setView('grid')}
            aria-label="Visualização em grade"
          >
            <LayoutGrid size={16} />
          </button>
          <button
            className={`btn ${view === 'list' ? 'btn-primary' : 'btn-ghost'}`}
            style={{ borderRadius: 0 }}
            onClick={() => setView('list')}
            aria-label="Visualização em lista"
          >
            <List size={16} />
          </button>
        </div>
      </div>

      {/* Count */}
      <div style={{ marginBottom: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        {loading ? '' : `${filtered.length} startup${filtered.length !== 1 ? 's' : ''} encontrada${filtered.length !== 1 ? 's' : ''}`}
      </div>

      {/* Content */}
      {loading ? (
        <div className="empty-state" style={{ minHeight: 300 }}>
          <Spinner size="lg" />
          <p>Carregando startups…</p>
        </div>
      ) : error ? (
        <div className="empty-state">
          <p className="text-error">{error}</p>
          <Button onClick={refetch} variant="secondary">Tentar novamente</Button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <p>Nenhuma startup encontrada com os filtros aplicados.</p>
          <Button onClick={() => { setSearch(''); setClassificationFilter(''); setLevelFilter(''); setStatusFilter(''); setCityFilter('') }} variant="secondary">
            Limpar filtros
          </Button>
        </div>
      ) : view === 'grid' ? (
        <motion.div
          className="grid grid-3"
          style={{ gap: '1rem' }}
          initial="hidden"
          animate="show"
          variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}
        >
          {filtered.map((s) => (
            <motion.div
              key={s.id}
              variants={{ hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } }}
            >
              <StartupCard startup={s} maturity={maturityMap[s.id]} />
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <StartupTable startups={filtered} maturityMap={maturityMap} />
      )}
    </motion.div>
  )
}
