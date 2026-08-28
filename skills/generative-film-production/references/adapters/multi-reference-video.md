# Multi-Reference Video Adapter

Bind each input to one role: identity, wardrobe, key prop/product, scene, style, or motion. State both `controls` and `does_not_control`. If the model supports fewer references than the spec, degrade by priority: identity > key prop/product > scene > style; carry lower-priority facts in text and report the degrade.
