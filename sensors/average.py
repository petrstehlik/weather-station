def average(vals):
	"""
	sort values, strip biggest and smallest and average the rest
	"""
	vals = sorted(vals)
	vals.pop()
	del vals[-1]

	avg = 0.0
	for i in vals:
		avg += i

	return (avg/float(len(vals)))
