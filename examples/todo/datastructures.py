
cartconfig = {
    'express': {
        'free_shipping_over': 22200,
        'shipping_costs': 1000,
    },
    'huWaWi': {
        'allow_anbruch': True
    }
}

cartconfig2 = dict(
    express =dict(
        free_shipping_over=22200,
        shipping_costs=1000,
    ),
    huWaWi=dict(
        allow_anbruch=True
    )
)

print cartconfig == cartconfig2
