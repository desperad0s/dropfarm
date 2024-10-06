"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Bar } from 'react-chartjs-2'
import {
	Chart as ChartJS,
	CategoryScale,
	LinearScale,
	BarElement,
	Title,
	Tooltip,
	Legend,
} from 'chart.js'
import { getEarningsData } from '@/lib/api'

ChartJS.register(
	CategoryScale,
	LinearScale,
	BarElement,
	Title,
	Tooltip,
	Legend
)

interface EarningsData {
	total: number
	lastMonth: number
	history: Array<{ date: string; amount: number }>
}

interface EarningsChartProps {
	earningsData?: EarningsData
}

export function EarningsChart({ earningsData }: EarningsChartProps) {
	if (!earningsData) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>Earnings</CardTitle>
				</CardHeader>
				<CardContent>
					<p>Loading earnings data...</p>
				</CardContent>
			</Card>
		)
	}

	const options = {
		responsive: true,
		plugins: {
			legend: {
				position: 'top' as const,
			},
			title: {
				display: true,
				text: 'Earnings Over Time',
			},
		},
	};

	const chartData = {
		labels: earningsData.history.map(d => d.date),
		datasets: [
			{
				label: 'Earnings',
				data: earningsData.history.map(d => d.amount),
				backgroundColor: 'rgba(75, 192, 192, 0.6)',
			},
		],
	};

	return (
		<Card>
			<CardHeader>
				<CardTitle>Earnings</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="h-[300px]">
					<Bar options={options} data={chartData} />
				</div>
				<div className="mt-4">
					<p>Total Earnings: ${earningsData.total.toFixed(2)}</p>
					<p>Last Month's Earnings: ${earningsData.lastMonth.toFixed(2)}</p>
				</div>
			</CardContent>
		</Card>
	);
}