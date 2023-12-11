import React from 'react';
import {Avatar, Box, Card, CardMedia, Chip, Rating, Stack, Typography} from "@mui/material";

export function MovieCard({title, release, description, image, rating, duration, genres, urls}) {
    const roundness = 4;
    const [hover, setHover] = React.useState(false);
    return (
        <Card
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
            sx={{
                width: 300,
                height: 500,
                padding: 0,
                margin: 1.6,
                marginBottom: 4,
                borderRadius: roundness,
                boxShadow: 4,
                position: 'relative',
                overflow: 'hidden', // Ensure the overflow is hidden for the gradient effect
                backgroundColor: 'black'
            }}>

            <Stack sx={{height: '100%'}}>
                <CardMedia
                    component="img"
                    sx={{
                        width: '100%',
                        height: '100%',
                        objectPosition: 'top',
                        objectFit: 'contain',
                        borderRadius: roundness,
                        borderBottomRightRadius: 0,
                        borderBottomLeftRadius: 0,
                        position: 'absolute',
                        zIndex: 10,
                        background: 'white!important'
                    }}
                    image={image}
                    alt="poster"
                />
                <Stack padding={1} paddingLeft={1.2} justifyItems={"flex-end"} flexGrow={1} sx={{
                    overflow: 'hidden',
                    color: 'white',
                    zIndex: 30,
                    height: '-webkit-fill-available',
                }}>
                    <Typography variant="title" component="h2"
                                sx={{fontWeight: 'bold', flexGrow: 1, display: 'flex', alignItems: 'flex-end'}}>
                        {title}
                    </Typography>
                    <Stack direction="row">
                        <Typography variant="body2" component="span"
                                    sx={{marginBottom: 0.8, fontSize: 14, marginLeft: 0.2, marginRight: 1}}> {release}
                        </Typography>
                        <Typography variant="body2" sx={{marginBottom: 0.8, fontSize: 14}}>|</Typography>
                        <Typography variant="body2" component="span"
                                    sx={{marginBottom: 0.8, fontSize: 14, marginX: 1}}> {duration}
                        </Typography>
                        <Typography variant="body2" sx={{marginBottom: 0.8, fontSize: 14}}>|</Typography>
                        <Rating name="read-only"
                                value={rating / 2}
                                precision={0.5}
                                size="small"
                                sx={{alignItems: 'start-end', marginLeft: 1}}
                                readOnly/>
                    </Stack>

                    <Stack direction="row" spacing={0.8}
                           sx={{overflowX: 'auto', marginBottom: 0.8, position: 'relative', zIndex: 30,}}>
                        {genres.map((genre) => (
                            <Chip label={genre} key={genre} size="small" variant="outlined" sx={{color: "#f5f5f5"}}/>
                        ))}
                    </Stack>
                    <Typography variant="body2" component="div" sx={{
                        marginBottom: 1,
                        fontSize: 12,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        '-webkit-line-clamp': hover ? '7' : '3',
                        '-webkit-box-orient': 'vertical',
                    }}>
                        {description}
                    </Typography>

                    {hover &&
                        <Stack>
                            <Typography variant="body2" component="div"
                                        sx={{marginLeft: 0.3, marginBottom: 0.5, fontSize: 14, fontWeight: 'bold'}}>
                                View on:
                            </Typography>
                            <Stack alignItems="flex-end" direction="row" spacing={1}
                                   sx={{position: 'relative', zIndex: 30}}>
                                {urls.map((url) => (
                                    <Chip avatar={<Avatar src={url.image}/>} component="button"
                                          label={url.name} clickable href={url.url} key={url} sx={{
                                        color: 'black',
                                        bgcolor: 'rgba(255,255,255,0.7)',
                                        borderColor: 'black',
                                        ':hover': {
                                            bgcolor: 'rgba(255,255,255,0.8)!important',
                                        }
                                    }}/>
                                ))}
                            </Stack>
                        </Stack>
                    }

                </Stack>

                <CardMedia
                    component="img"
                    sx={{
                        display: rating < 5 || rating > 8 ? 'block' : 'none',
                        marginLeft: rating > 8 ? 20 : 20,
                        marginTop: rating > 8 ? 34 : 40,
                        width: rating > 8 ? 200 : 150,
                        height: rating > 8 ? 300 : 160,
                        opacity: 0.4,
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        zIndex: 25,
                    }}
                    image={rating > 8 ? "../../public/fire.png" : rating > 5 ? null : "../../public/fish.png"}
                />

                {/* Gradient overlay for fading effect on the edges */}
                <Box
                    className="gradient-overlay"
                    sx={{
                        position: 'absolute',
                        opacity: 1,
                        transition: 'all 0.3s',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        zIndex: 20,
                        background: 'linear-gradient(0deg, rgba(0,0,0,1) 0 25%, rgba(0,0,0,0))',
                    }}
                />
                <Box
                    className="gradient-overlay-hover"
                    sx={{
                        position: 'absolute',
                        opacity: hover ? 1 : 0,
                        transition: 'all 0.3s',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        zIndex: 20,
                        background: 'linear-gradient(0deg, rgba(0,0,0,1) 0 30%, rgba(0,0,0,0))',
                    }}
                />

            </Stack>
        </Card>
    )
}
